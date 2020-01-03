import argparse

import boto3
import yaml

parser = argparse.ArgumentParser()
parser.add_argument("tags", help="Specify which comma separated tags to scan for.")
parser.add_argument("-r", "--region", help="Specify AWS region. Default is us-east-1.", default="us-east-1")
parser.add_argument("-w", "--write", help="Write tags to the service. Default is false.", action="store_true")
parser.add_argument("-f", "--file", help="file which holds the mappings to write", default="tag_config.yaml")
parser.add_argument("-d", "--dry-run", help="simulate a dry run", action="store_true")
parser.add_argument("-o", "--overwrite", help="write the tag even if it is already set", action="store_true")
args = parser.parse_args()

region = args.region
target_tags = args.tags.split(",")

client = boto3.client('lambda', region)

print(f"Loading functions for region {region}")
functions = client.list_functions().get('Functions', [])

if args.write:
    with open(args.file) as file:
        tags_config = yaml.load(file)
        for target_tag in target_tags:
            if target_tag not in tags_config:
                print(f"{target_tag} is missing from the yaml file. Please add it to the file or omit the tag. Aborting.")
                exit()

for function in functions:
    print('-----')
    print(f"Loading tags for function {function['FunctionArn']}")
    function_tags = client.list_tags(Resource=function['FunctionArn']).get('Tags', [])
    print(f"Found {len(function_tags)} tags: {function_tags}")

    for target_tag in target_tags:
        print(f"Processing tag '{target_tag}'.")
        if target_tag not in function_tags or args.overwrite:
            if not args.overwrite:
                print(f"Function {function['FunctionArn']} is missing tag '{target_tag}'")

            if args.write:
                new_tags = {}
                if target_tag in tags_config and tags_config[target_tag] is not None:
                    for tag_value, arn_parts in tags_config[target_tag].items():
                        for arn_part in arn_parts:
                            if arn_part in function['FunctionArn']:
                                new_tags[target_tag] = tag_value
                else:
                    print(f"Tag {target_tag} has no values in the yaml file.")

                if len(new_tags) > 0:
                    print(f"Adding tags to function {function['FunctionArn']}: {new_tags}")
                    if not args.dry:
                        client.tag_resource(Resource=function['FunctionArn'], Tags=new_tags)
                else:
                    print(f"No new tags for function {function['FunctionArn']}")
            else:
                print("Write is disabled. Tags are not updated. Use --write to activate it. Use --write AND --dry-run for a dry run.")
        else:
            print(f"Function already has the tag {target_tag}.")
