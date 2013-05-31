from datetime import datetime

from flask import request

from moxie.core.views import ServiceView, accepts
from moxie.core.exceptions import abort
from moxie.core.representations import HAL_JSON, JSON

from .services import EventsService
from .representations import HALEventRepresentation, HALEventsRepresentation


class EventsToday(ServiceView):

    def handle_request(self):
        service = EventsService.from_context()
        return service.get_events_for_day(datetime.today())

    @accepts(JSON, HAL_JSON)
    def as_json(self, response):
        return HALEventsRepresentation(response, request.path).as_json()


class EventsForDate(ServiceView):

    def handle_request(self, year, month, day):
        service = EventsService.from_context()
        try:
            date = datetime(int(year), int(month), int(day))
        except ValueError as ve:
            return abort(400, ve.message)
        return service.get_events_for_day(date)

    @accepts(JSON, HAL_JSON)
    def as_json(self, response):
        return HALEventsRepresentation(response, request.path).as_json()


class EventView(ServiceView):

    def handle_request(self, uid):
        service = EventsService.from_context()
        return service.get_event(uid)

    @accepts(JSON, HAL_JSON)
    def as_json(self, response):
        return HALEventRepresentation(response, request.url_rule.endpoint).as_json()