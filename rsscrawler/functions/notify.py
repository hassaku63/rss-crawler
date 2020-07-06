import json
from decimal import Decimal
from rsscrawler.libs import queue
from rsscrawler.libs.dynamodb import get_table
from rsscrawler.libs.rss import TechplayFeedRepository
from rsscrawler.libs.slack import create_slack_client
from rsscrawler import settings

from rsscrawler.log import get_logger
log = get_logger(__name__)


def handler(event, context):
    log.info(event)
    table = get_table(settings.RSS_TABLE_NAME)
    # is_
    response = table.query(
        IndexName=settings.RSS_TABLE_GSI,
        Select='ALL_ATTRIBUTES',
        Limit=10,
        KeyConditionExpression='is_notified = :isnotif and begins_with(source_rss, :srcrss)',
        ExpressionAttributeValues={
            ':isnotif': 0,
            ':srcrss': 'Connpass'
        }
    )

    block_text = ''
    for item in response.get('Items', []):
        block_text += f'- <{item["link"]}|{item["title"]}>\n'
        updated_response = table.update_item(
            Key={
                'rss_id': item['rss_id']
            },
            UpdateExpression='set is_notified=:isnotif',
            ExpressionAttributeValues={
                ':isnotif': item['is_notified'] + Decimal(1)
            },
            ReturnValues='ALL_NEW',
        )
        log.info(updated_response)
    
    slk = create_slack_client()
    slk.post(blocks=[{
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': 'Connpass feeds'
        }
    }, {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': 'no items.' if block_text == '' else block_text
        }
    }])


if __name__ == '__main__':
    # Reset
    table = get_table(settings.RSS_TABLE_NAME)
    items = table.scan()['Items']
    for item in items: 
        table.update_item(
            Key={'rss_id': item['rss_id']}, 
            UpdateExpression='set is_notified=:isnotif', 
            ExpressionAttributeValues={
                ':isnotif': Decimal(0)
            },
            ReturnValues='ALL_NEW'
        )

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