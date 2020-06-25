import boto3
from rsscrawler import settings

resource = None


def _get_resource():
    global resource
    if resource is None:
        resource = boto3.resource('dynamodb')
    return resource


def get_table(name):
    return _get_resource().Table(name)