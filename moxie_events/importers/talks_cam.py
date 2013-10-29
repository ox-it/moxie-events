from datetime import datetime
from lxml import etree
import logging
from StringIO import StringIO

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
            data, encoding = self.retrieve_feed(feed)
            self.indexer.index(self.index_feed(data, encoding))

    def retrieve_feed(self, url):
        try:
            response = requests.get(url, timeout=self.FETCH_TIMEOUT)
            response.raise_for_status()
            return response.content, response.encoding
        except RequestException as re:
            logger.error('Error fetching events (TalksCam)', exc_info=True,
                         extra={
                             'data': {
                                 'url': url}
                         })
            raise re

    def index_feed(self, data, encoding):
        """Index talks in given feed
        :param url: URL of the feed
        :return: list of events
        """
        parser = etree.XMLParser(ns_clean=True,recover=True,encoding=encoding)
        xml = etree.parse(StringIO(data), parser)
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
        description = talk.find('abstract')
        if description is not None and description.text:
            event.description = description.text.strip()
        event.source_url = talk.find('url').text
        event.start_time = self.parse_date(talk.find('start_time').text)
        end_time = talk.find('end_time')
        if end_time is not None:
            event.end_time = self.parse_date(end_time.text)
        else:
            # if there is no end time, defaults to the start time
            event.end_time = event.start_time
        location = talk.find('venue')
        if location is not None:
            event.location = location.text.strip()
        return event.to_solr_dict()

    def parse_date(self, date):
        """Parse date as Tue, 21 Feb 2012 23:49:34 +0000
        """
        return datetime.strptime(date[:-6], "%a, %d %b %Y %H:%M:%S")