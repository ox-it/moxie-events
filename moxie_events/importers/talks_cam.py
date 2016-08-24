from datetime import datetime
from dateutil import parser
from lxml import etree
import json
import logging
from StringIO import StringIO

import requests
from requests import RequestException

from moxie_events.domain import Event

logger = logging.getLogger(__name__)


class TalksCamEventsImporter(object):

    FETCH_TIMEOUT = 30

    def __init__(self, feeds, indexer):
        self.feeds = feeds
        self.indexer = indexer

    def run(self):
        for feed in self.feeds:
            data, encoding = self.retrieve_feed(feed)
            events = self.index_feed(data, encoding)
            self.indexer.index(events)

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
        response = json.loads(data)
        talks = []
        for talk in response['_embedded']['talks']:
            try:
                talks.append(self.parse_talk(talk))
            except Exception as e:
                logger.error("Couldn't parse talk", exc_info=True)
        
        return talks
        

    def parse_talk(self, talk):
        """Parse an XML "talk"
        :param xml: talk object
        :return: Event object
        """
        event = Event(talk['slug'])
        event.id = talk['slug']
        event.name = talk['title_display']
        event.source_url = talk['_links']['self']['href']
        event.start_time = self.parse_date(talk['start'])
        event.end_time = self.parse_date(talk['end'])
        if 'location_summary' in talk:
            event.location = talk['location_summary']
        
        solr_dict = event.to_solr_dict()
        return solr_dict

    def parse_date(self, date):
        """Parse date as ISO. e.g 2016-07-14T10:30:00+01:00
        """
        return parser.parse(date)
        
        
