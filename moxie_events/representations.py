from flask import url_for, jsonify

from moxie.core.representations import Representation, HALRepresentation


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
            'start_time': self.event.start_time,
            'end_time': self.event.end_time,
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
        representation.add_link('self', url_for(self.endpoint, ident=self.event.uid))
        return representation.as_dict()


class HALEventsRepresentation(object):

    def __init__(self, events, endpoint):
        self.events = events
        self.endpoint = endpoint

    def as_json(self):
        return jsonify(self.as_dict())

    def as_dict(self):
        representation = HALRepresentation({})
        representation.add_embed('events', [HALEventRepresentation(e, 'events.event').as_dict()
                                            for e in self.events])
        representation.add_link('self', url_for('events.today'))
        return representation.as_dict()
