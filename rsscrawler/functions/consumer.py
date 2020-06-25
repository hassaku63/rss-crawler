import json
from botocore.exceptions import ClientError
from rsscrawler.libs import queue
from rsscrawler.libs.dynamodb import get_table
from rsscrawler import settings

from rsscrawler.log import get_logger
log = get_logger(__name__)


# @queue.from_sqs_each
def handler(event, context):
    # TODO: 冪等性担保の仕組み
    # log.info(event)
    for record in event['Records']:
        body = json.loads(record['body'])
        log.info(body)
        table = get_table(settings.RSS_TABLE_NAME)
        for entry in body.get('entries', []):
            try:
                res = table.put_item(
                    Item={
                        'rss_id': entry['id'],
                        'title': entry['title'],
                        'link': entry['link'],
                        'source_rss': body['name'].split('/')[0],
                        'name': body['name'],
                        'is_notified': 0 # False
                    },
                    ConditionExpression='attribute_not_exists(rss_id)',
                    ReturnValues='ALL_OLD'
                )
                # log.info(res)
            except ClientError as e:
                if e.response['Error']['Code']=='ConditionalCheckFailedException':
                    log.info({
                        'event': 'DynamoDB ConditionalWrite check failed',
                        'rss_id': entry['id'],
                        'message': str(e)
                    }) 

if __name__ == '__main__':
    handler({
        "Records": [
            {
                "messageId":  "19dd0b57-b21e-4ac1-bd88-01bbb068cb78",
                "receiptHandle": "MessageReceiptHandle",
                "body": json.dumps([
                    {'id': 1},
                    {'id': 2}
                ]),
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1523232000000",
                    "SenderId": "123456789012",
                    "ApproximateFirstReceiveTimestamp": "1523232000001"
                },
                "messageAttributes": {},
                "md5OfBody":  "7b270e59b47ff90a553787216d55d91d",
                "eventSource": "aws:sqs",
                "eventSourceARN":     "arn:aws:sqs:ap-northeast-1:123456789012:MyQueue",
                "awsRegion": "ap-northeast-1"
            }
        ]
    }, {})