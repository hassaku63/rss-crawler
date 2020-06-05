import re
import feedparser
from rsscrawler import settings

from rsscrawler.log import get_logger
log = get_logger(__name__)


def _escape_text(s: str):
    """Escape characters <, >, &

    https://api.slack.com/reference/surfaces/formatting#escaping
    """
    result = s.replace('<', '&lt;')
    result = result.replace('>', '&gt;')
    result = result.replace('&', '&amp;')
    return result


class TargetFeedRepository(object):
    def get_feed_title(self):
        raise NotImplementedError

    def fetch(self):
        raise NotImplementedError
    
    def to_slack_block(self):
        raise NotImplementedError


class TechplayFeedRepository(TargetFeedRepository):
    def __init__(self):
        self.feeds = []
        self.feed_url = 'https://rss.techplay.jp/event/w3c-rss-format/rss.xml'
        self.eventplace = [
            'オンライン',
            'online',
            'Online'
        ]
        self.filters = [
            re.compile(r'python', flags=re.IGNORECASE),
            re.compile(r'機械学習', flags=re.IGNORECASE),
            re.compile(r'AI', flags=re.IGNORECASE),
            re.compile(r'ディープラーニング'),
            re.compile(r'AWS', flags=re.IGNORECASE),
            re.compile(r'typescript', flags=re.IGNORECASE),
            re.compile(r'javascript', flags=re.IGNORECASE),
            re.compile(r'ruby', flags=re.IGNORECASE),
            re.compile(r'SRE', flags=re.IGNORECASE),
            re.compile(r'DevOps', flags=re.IGNORECASE),
            re.compile(r'serverless', flags=re.IGNORECASE),
            re.compile(r'サーバーレス', flags=re.IGNORECASE),
            re.compile(r'コンテナ', flags=re.IGNORECASE),
            re.compile(r'Kubernates', flags=re.IGNORECASE),
            re.compile(r'GCP', flags=re.IGNORECASE),
            re.compile(r'Azure', flags=re.IGNORECASE),
            re.compile(r'統計', flags=re.IGNORECASE),
            re.compile(r'CI', flags=re.IGNORECASE),
            re.compile(r'CD', flags=re.IGNORECASE),
            re.compile(r'GraphQL', flags=re.IGNORECASE),
        ]

    def get_feed_title(self):
        return 'TECH_PLAY'

    def _filter(self, feeds):
        result = []
        for ent in self.feeds.entries:
            if not ent.tp_eventplace in self.eventplace:
                continue
            for regexp in self.filters:
                if regexp.search(str(ent.title)) or regexp.search(str(ent.summary)):
                    result.append(ent)
                    break
        return result

    def _sort_by_published(self, feeds):
        pass

    def _sort_by_starttime(self, feeds):
        pass

    def fetch(self):
        self.feeds = feedparser.parse(self.feed_url)

    def to_slack_block(self):
        """
        Execute fetch method before call this.
        """
        feeds = self._filter(self.feeds)
        result = []
        text = ''
        for feed in feeds:
            text += f'* {feed.tp_eventstarttime} <{feed.link}|{_escape_text(feed.title)}>\n'
        result.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': text
            }
        })
        return result


if __name__ == '__main__':
    import json
    from slack import WebClient
    contents = []
    # for config in settings.RSS_CONFIG:
    #     ret = feedparser.parse(config['feed_url'])
    #     filters = config.get('filters', [])
    #     for filter in filters:
    #         pass
    #     # contents.append()
    techplay = TechplayFeedRepository()
    
    techplay.fetch()
    render_data = techplay.to_slack_block()
    print(json.dumps(render_data, indent=2, ensure_ascii=False))

    slk = WebClient(token=settings.SLACK_BOT_TOKEN)
    slk.chat_postMessage(blocks=render_data, channel=settings.SLACK_CHANNEL)

    # regexps = [
    #     re.compile(r'python', flags=re.IGNORECASE),
    #     re.compile(r'機械学習', flags=re.IGNORECASE),
    #     re.compile(r'AI', flags=re.IGNORECASE),
    #     re.compile(r'ディープラーニング'),
    #     re.compile(r'AWS', flags=re.IGNORECASE),
    #     re.compile(r'typescript', flags=re.IGNORECASE),
    #     re.compile(r'SRE', flags=re.IGNORECASE),
    #     re.compile(r'DevOps', flags=re.IGNORECASE),
    # ]
    # for ent in techplay.feeds.entries:
    #     # print(ent.title)
    #     for regexp in regexps:
    #         if regexp.search(str(ent.title)):
    #             print(ent.title)
    #             break