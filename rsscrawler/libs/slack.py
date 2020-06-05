from slack import WebClient
from rsscrawler import settings

from rsscrawler.log import get_logger
log = get_logger(__name__)


class Slack(object):
    def __init__(self):
        self.client: WebClient
        self.channel: str
    
    def set_channel(self, channel: str):
        self.channel = channel

    def set_client(self, client: WebClient):
        self.client = client
    
    def post(self, blocks):
        log.info(blocks)
        self.client.chat_postMessage(
            blocks=blocks,
            channel=self.channel
        )


def create_slack_client():
    slk = Slack()
    slk.set_channel(settings.SLACK_CHANNEL)
    slk.set_client(WebClient(token=settings.SLACK_BOT_TOKEN))
    return slk