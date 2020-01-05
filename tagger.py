import argparse
import yaml

from client import Client

parser = argparse.ArgumentParser()
parser.add_argument("service", help="Specify which AWS service to use. Currently supported: lambda, cloudwatchlogs")
parser.add_argument("tags", help="Specify which comma separated tags to scan for.")
parser.add_argument("-r", "--region", help="Specify AWS region. Default is us-east-1.", default="us-east-1")
parser.add_argument("-w", "--write", help="Write tags to the service. Default is false.", action="store_true")
parser.add_argument("-f", "--file", help="file which holds the mappings to write", default="tag_config.yaml")
parser.add_argument("-d", "--dry-run", help="simulate a dry run", action="store_true")
parser.add_argument("-o", "--overwrite", help="write the tag even if it is already set", action="store_true")
args = parser.parse_args()

target_tags = args.tags.split(",")
target_tags.sort()

client = Client(args.service, args.region)
print(f"Loading resources for service {args.service} and region '{args.region}'")
resources = client.get_resources()
print(f"Loaded {len(resources)} resources.")

if args.write:
    with open(args.file) as file:
        tags_config = yaml.load(file)
        for target_tag in target_tags:
            if target_tag not in tags_config:
                print(f"'{target_tag}' is missing from the yaml file. Please add it to the file or omit the tag. Aborting.")
                exit()

untagged_count = 0
for resource in resources:
    print('-----')
    print(f"Loading tags for resource {resource['tagger_id']}")
    resource_tags = client.get_tags(resource['tagger_id'])
    print(f"Found {len(resource_tags)} tags: {resource_tags}")

    for target_tag in target_tags:
        print(f"Processing tag '{target_tag}'.")
        if target_tag not in resource_tags or args.overwrite:
            if not args.overwrite:
                print(f"Resource {resource['tagger_id']} is missing tag '{target_tag}'.")

            if args.write:
                new_tags = {}
                if target_tag in tags_config and tags_config[target_tag] is not None:
                    for tag_value, arn_parts in tags_config[target_tag].items():
                        if arn_parts is None:
                            print(f"The tag '{target_tag}'s value {tag_value} has no arn_parts in the yaml file.")
                            continue
                        arn_parts.sort()
                        for arn_part in arn_parts:
                            if arn_part in resource['tagger_id']:
                                new_tags[target_tag] = tag_value
                else:
                    print(f"Tag '{target_tag}' has no values in the yaml file.")

                if len(new_tags) > 0:
                    print(f"Adding tags to resource {resource['tagger_id']}: {new_tags}")
                    if not args.dry_run:
                        client.write_tags(resource['tagger_id'], new_tags)
                else:
                    print(f"No new tags for resource {resource['tagger_id']}.")
            else:
                print("Write is disabled. Tags are not updated. Use --write to activate it. Use --write AND --dry-run for a dry run.")
                untagged_count += 1
        else:
            print(f"Function already has the tag '{target_tag}'.")

print('--- DONE ---')
if untagged_count > 0:
    print(f"{untagged_count} resources remain untagged.")