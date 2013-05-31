from datetime import datetime

SOLR_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class Event(object):
    def __init__(self, uid):
        """Event
        :param uid: unique identifier of the event
        """
        self.uid = uid

    uid = None

    name = None

    description = None

    location = None

    start_time = None

    end_time = None

    source_url = None

    def to_solr_dict(self):
        """Get event as a dict with Solr keys
        :return: dict
        """
        data = {
            'source_name': self.source_url,
            'source_url': self.source_url,
            'event_uid': self.uid,
            'event_title': self.name,
            'event_description': self.description,
            'event_start': self._date_to_solr(self.start_time),
            'event_end': self._date_to_solr(self.end_time)
        }
        if self.location:
            data['event_location'] = self.location
        return data

    @staticmethod
    def from_solr_dict(d):
        """Get an Event domain object from a Solr response
        :param d: dict with Solr values
        :return: Event domain object
        """
        event = Event(d['event_uid'])
        event.source_url = d['source_url']
        event.name = d['event_title']
        event.description = d['event_description']
        event.start_time = Event._parse_date(d['event_start'])
        event.end_time = Event._parse_date(d['event_end'])
        if 'event_location' in d:
            event.location = d['event_location']
        return event

    @staticmethod
    def _parse_date(date):
        """Parse date from Solr format
        :param date: str (date from Solr)
        :return: datetime object
        """
        return datetime.strptime(date, SOLR_DATE_FORMAT)

    @staticmethod
    def _date_to_solr(date):
        """Get the date in Solr format
        :param date: datetime object
        :return: str (date in Solr format)
        """
        return date.strftime(SOLR_DATE_FORMAT)