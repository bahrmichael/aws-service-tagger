import boto3

CLOUDFRONT = 'cloudfront'
CLOUDWATCHLOGS = 'cloudwatchlogs'
LAMBDA = 'lambda'


class Client:

    def __init__(self, service, region):
        self.service = service
        self.region = region

        if self.service == LAMBDA:
            self.client = boto3.client('lambda', self.region)
        elif self.service == CLOUDWATCHLOGS:
            self.client = boto3.client('logs', self.region)
        elif self.service == CLOUDFRONT:
            self.client = boto3.client('cloudfront', self.region)
        else:
            raise Exception(f'Service {self.service} is not yet supported.')

    def get_resources(self):
        resources = []
        if self.service == LAMBDA:
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Paginator.ListFunctions
            for page in self.client.get_paginator('list_functions').paginate():
                resources.extend(page.get('Functions'))
            resources.sort(key=lambda x: x['FunctionArn'])
            for r in resources:
                r['tagger_id'] = r['FunctionArn']
        elif self.service == CLOUDWATCHLOGS:
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Paginator.DescribeLogGroups
            for page in self.client.get_paginator('describe_log_groups').paginate():
                resources.extend(page.get('logGroups'))
            resources.sort(key=lambda x: x['logGroupName'])
            for r in resources:
                r['tagger_id'] = r['logGroupName']
        elif self.service == CLOUDFRONT:
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront.html#CloudFront.Client.list_distributions
            for page in self.client.get_paginator('list_distributions').paginate():
                resources.extend(page.get('DistributionList', {}).get('Items', []))
            resources.sort(key=lambda x: x['ARN'])
            for r in resources:
                r['tagger_id'] = r['ARN']
        return resources

    def get_tags(self, tagger_id):
        if self.service == LAMBDA:
            return self.client.list_tags(Resource=tagger_id).get('Tags', [])
        elif self.service == CLOUDWATCHLOGS:
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.list_tags_log_group
            return self.client.list_tags_log_group(logGroupName=tagger_id).get('tags', [])
        elif self.service == CLOUDFRONT:
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront.html#CloudFront.Client.list_tags_for_resource
            result = {}
            for item in self.client.list_tags_for_resource(Resource=tagger_id).get('Tags', {}).get('Items', []):
                result[item['Key']] = item['Value']
            return result

    def write_tags(self, tagger_id, new_tags):
        if self.service == LAMBDA:
            self.client.tag_resource(Resource=tagger_id, Tags=new_tags)
        elif self.service == CLOUDWATCHLOGS:
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.tag_log_group
            self.client.tag_log_group(logGroupName=tagger_id, tags=new_tags)
        elif self.service == CLOUDFRONT:
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront.html#CloudFront.Client.tag_resource
            items = []
            for key, value in new_tags.items():
                items.append({
                    'Key': key,
                    'Value': value
                })
            self.client.tag_resource(Resource=tagger_id, Tags={'Items': items})
