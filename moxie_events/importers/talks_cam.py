from datetime import datetime
from lxml import etree
import logging
import requests
from requests import RequestException

from moxie_events.domain import Event

logger = logging.getLogger(__name__)


class TalksCamEventsImporter(object):

    FETCH_TIMEOUT = 2

    def __init__(self, feeds, indexer):
        self.feeds = feeds
        self.indexer = indexer

    def run(self):
        for feed in self.feeds:
            data = self.retrieve_feed(feed)
            if data:
                self.indexer.index(self.index_feed(data))

    def retrieve_feed(self, url):
        try:
            response = requests.get(url, timeout=self.FETCH_TIMEOUT, config={'danger_mode': True})
            return response.text
        except RequestException as re:
            logger.warning('Error fetching events (TalksCam)', exc_info=True,
                           extra={
                               'data': {
                                   'url': url}
                           })
            return None

    def index_feed(self, data):
        """Index talks in given feed
        :param url: URL of the feed
        :return: list of events
        """
        xml = etree.parse(data)
        talks = []
        for talk in xml.findall('talk'):
            try:
                talks.append(self.parse_talk(talk))
            except:
                logger.error("Couldn't parse talk", exc_info=True)
        return talks

    def parse_talk(self, talk):
        """Parse an XML "talk"
        :param xml: talk object
        :return: Event object
        """
        event = Event(talk.find('id').text)
        event.name = talk.find('title').text.strip()
        description = talk.find('abstract').text
        if description:
            event.description = description.strip()
        event.source_url = talk.find('url').text
        event.start_time = self.parse_date(talk.find('start_time').text)
        event.end_time = self.parse_date(talk.find('start_time').text)
        event.location = talk.find('venue').text.strip()
        return event.to_solr_dict()

    def parse_date(self, date):
        """Parse date as Tue, 21 Feb 2012 23:49:34 +0000
        """
        return datetime.strptime(date[:-6], "%a, %d %b %Y %H:%M:%S")