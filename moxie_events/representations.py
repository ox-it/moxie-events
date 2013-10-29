from flask import url_for, jsonify
from icalendar import Calendar, Event

from moxie.core.representations import Representation, HALRepresentation, get_nav_links


class EventRepresentation(Representation):

    def __init__(self, event):
        self.event = event

    def as_json(self):
        return jsonify(self.as_dict())

    def as_dict(self):
        return {
            'id': self.event.uid,
            'name': self.event.name,
            'description': self.event.description,
            'location': self.event.location,
            'start_time': self.event.start_time.isoformat(),
            'end_time': self.event.end_time.isoformat(),
            'source_url': self.event.source_url,
            'signature': self.event.signature,      # signature is a hash of the event which defines its uniqueness
        }


class HALEventRepresentation(EventRepresentation):

    def __init__(self, event, endpoint):
        super(HALEventRepresentation, self).__init__(event)
        self.endpoint = endpoint

    def as_json(self):
        return jsonify(self.as_dict())

    def as_dict(self):
        base = super(HALEventRepresentation, self).as_dict()
        representation = HALRepresentation(base)
        representation.add_link('self', url_for(self.endpoint, ident=self.event.signature))
        return representation.as_dict()


class ICalEventRepresentation(EventRepresentation):

    def as_event_ical(self):
        event = Event()
        event.add('summary', self.event.name)
        event.add('dtstart', self.event.start_time)
        event.add('dtend', self.event.end_time)
        event.add('description', self.event.description)
        event.add('location', self.event.location)
        event['uid'] = self.event.signature
        return event

    def as_ical(self):
        cal = Calendar()
        cal.add('prodid', '-github.com/ox-it/moxie-events-')
        cal.add('version', '2.0')
        event = self.as_event_ical()
        cal.add_component(event)
        return cal.to_ical()


class HALEventsRepresentation(object):

    def __init__(self, events, endpoint, start, count, size, day=None, month=None, year=None):
        self.events = events
        self.endpoint = endpoint
        self.start = start
        self.count = count
        self.size = size
        self.day = day
        self.month = month
        self.year = year

    def as_json(self):
        return jsonify(self.as_dict())

    def as_dict(self):
        representation = HALRepresentation({})
        representation.add_embed('events', [HALEventRepresentation(e, 'events.event').as_dict()
                                            for e in self.events])
        if self.day and self.month and self.year:
            representation.add_links(get_nav_links(self.endpoint, self.start, self.count, self.size,
                                                   day=self.day, month=self.month, year=self.year))
            representation.add_link('self', url_for(self.endpoint, day=self.day, month=self.month, year=self.year))
        else:
            representation.add_links(get_nav_links(self.endpoint, self.start, self.count, self.size))
            representation.add_link('self', url_for(self.endpoint))
        return representation.as_dict()


class ICalEventsRepresentation(object):

    def __init__(self, events):
        self.events = events

    def as_ical(self):
        cal = Calendar()
        cal.add('prodid', '-github.com/ox-it/moxie-events-')
        cal.add('version', '2.0')
        for event in self.events:
            vevent = ICalEventRepresentation(event).as_event_ical()
            cal.add_component(vevent)
        return cal.to_ical()
