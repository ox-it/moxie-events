from flask import url_for, jsonify

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
            'source_url': self.event.source_url
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
