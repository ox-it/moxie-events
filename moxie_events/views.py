from datetime import datetime

from flask import request

from moxie.core.views import ServiceView, accepts
from moxie.core.exceptions import abort
from werkzeug.wrappers import BaseResponse
from moxie.core.representations import HAL_JSON, JSON

from .services import EventsService
from .representations import HALEventRepresentation, HALEventsRepresentation


class EventsToday(ServiceView):

    def handle_request(self):
        service = EventsService.from_context()
        self.start = request.args.get('start', 0)
        self.count = request.args.get('count', 35)
        results, self.size = service.get_events_for_day(datetime.today(), self.start, self.count)
        return results

    @accepts(JSON, HAL_JSON)
    def as_json(self, response):
        return HALEventsRepresentation(response, request.url_rule.endpoint, self.start, self.count, self.size).as_json()


class EventsForDate(ServiceView):

    def handle_request(self, year, month, day):
        service = EventsService.from_context()
        self.start = request.args.get('start', 0)
        self.count = request.args.get('count', 35)
        self.year = year
        self.month = month
        self.day = day
        try:
            date = datetime(int(year), int(month), int(day))
        except ValueError as ve:
            return abort(400, ve.message)
        else:
            results, self.size = service.get_events_for_day(date, self.start, self.count)
            return results

    @accepts(JSON, HAL_JSON)
    def as_json(self, response):
        if issubclass(type(response), BaseResponse):
            return response
        else:
            return HALEventsRepresentation(response, request.url_rule.endpoint, self.start, self.count, self.size,
                                           day=self.day, month=self.month, year=self.year).as_json()


class EventView(ServiceView):

    def handle_request(self, ident):
        service = EventsService.from_context()
        event = service.get_event(ident)
        if event:
            return event
        else:
            return abort(404)

    @accepts(JSON, HAL_JSON)
    def as_json(self, response):
        if issubclass(type(response), BaseResponse):
            # to handle 301 redirections and 404
            return response
        else:
            return HALEventRepresentation(response, request.url_rule.endpoint).as_json()