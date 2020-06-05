import json
from rsscrawler.libs.rss import TechplayFeedRepository
from rsscrawler.libs.slack import create_slack_client

from rsscrawler.log import get_logger
log = get_logger(__name__)


def handler(event, context):
    techplay = TechplayFeedRepository()
    slk = create_slack_client()

    techplay.fetch()
    blocks = techplay.to_slack_block()
    log.info(msg=json.dumps(blocks))
    slk.post(blocks)


if __name__ == '__main__':
    pass
    # handler({}, {})