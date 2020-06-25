import json
from functools import wraps
import boto3

from rsscrawler import settings
from rsscrawler.log import get_logger
log = get_logger(__name__)


sqs_client = None


def _get_queue_url(account, region, queue_name):
    log.info({
        'event': '_get_queue_url',
        'message': f'https://sqs.{region}.amazonaws.com/{account}/{queue_name}'
    })
    return f'https://sqs.{region}.amazonaws.com/{account}/{queue_name}'


def _get_sqs_client():
    global sqs_client
    if sqs_client is None:
        sqs_client = boto3.client('sqs')
    return sqs_client


def _send_message(queue_url: str, message):
    sqs = _get_sqs_client()
    return sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=message
    )


def send_rss(message):
    """Send message to RSS Queue

    :param message: JSON Seriarizable object
    :type message: object
    :return: MessageId
    :rtype: str
    """
    result = _send_message(
        queue_url=_get_queue_url(
            account=settings.AWS_ACCOUNT_ID,
            region=settings.AWS_REGION,
            queue_name=settings.RSS_QUEUE_NAME
        ),
        message=json.dumps(message, ensure_ascii=False)
    )
    return result['MessageId']


def done(receipy_handle):
    """Remove message from queue

    :param receipy_handle: queue
    :type receipy_handle: str
    :return: RequestId of delete_message
    :rtype: str
    """
    sqs = _get_sqs_client()
    result = sqs.delete_message(
        QueueUrl=_get_queue_url(
            account=settings.AWS_ACCOUNT_ID,
            region=settings.AWS_REGION,
            queue_name=settings.RSS_QUEUE_NAME
        ),
        ReceiptHandle=receipy_handle
    )
    return result['ResponseMetadata']['RequestId']


def from_sqs_each(func):
    """Decorator for lambda handler

    :param func: lambda handler function
    :type func: function
    """
    @wraps(func)
    def wrapper(data, context={}, *args, **kwargs):
        log.info(data)
        for record in data['Records']:
            try:
                record['body'] = json.loads(record['body'])
                log.info(f"queue_record={record}")
                func(record, context)
                done(record['receiptHandle'])
            except Exception as e:
                log.error(str(e))
    return wrapper