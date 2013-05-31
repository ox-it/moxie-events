import requests
import datetime
from lxml import etree
from moxie_events.domain import Event


class TalksCamEventsImporter(object):

    FETCH_TIMEOUT = 2

    def __init__(self, feeds, indexer):
        self.feeds = feeds
        self.indexer = indexer

    def run(self):
        for feed in self.feeds:
            self.indexer.index(self.index_feed(feed))

    def index_feed(self, url):
        """Index talks in given feed
        :param url: URL of the feed
        :return: list of events
        """
        feed = requests.get(url, timeout=self.FETCH_TIMEOUT).text
        xml = etree.parse(feed)
        talks = []
        for talk in xml.findall('talk'):
            talks.append(self.parse_talk(talk))
        return talks

    def parse_talk(self, talk):
        """Parse an XML "talk"
        :param xml: talk object
        :return: Event object
        """
        event = Event(talk.find('id'))
        event.name = talk.find('title').text.strip()
        event.description = talk.find('abstract').text.strip()
        event.source_url = talk.find('url').text
        event.start_time = self.parse_date(talk.find('start_time').text)
        event.end_time = self.parse_date(talk.find('start_time').text)
        event.location = talk.find('venue').text.strip()
        return event

    def parse_date(self, date):
        """Parse date as Tue, 21 Feb 2012 23:49:34 +0000
        """
        return datetime.strptime(date[:-6], "%a, %d %b %Y %H:%M:%S")