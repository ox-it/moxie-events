from datetime import datetime, timedelta

from flask import request

from moxie.core.views import ServiceView, accepts
from moxie.core.cache import cache, args_cache_key
from moxie.core.exceptions import BadRequest, NotFound
from werkzeug.wrappers import BaseResponse
from moxie.core.representations import HAL_JSON, JSON

from .services import EventsService
from .representations import HALEventRepresentation, HALEventsRepresentation


class EventsSearch(ServiceView):

    @cache.cached(timeout=600, key_prefix=args_cache_key)
    def handle_request(self):
        service = EventsService.from_context()
        start = request.args.get('start', 0)
        count = request.args.get('count', 35)
        dt_start = request.args.get('from', None)
        dt_end = request.args.get('to', None)

        if not dt_start:
            raise BadRequest("Parameter 'from' is mandatory (e.g. 2012-12-12)")

        if dt_start == "now":
            dt_start = datetime.now()
        else:
            try:
                dt_start = to_datetime(dt_start, 0, 0)
            except ValueError as ve:
                raise BadRequest("Parameter 'from': value error: {m}".format(m=ve.message))

        if dt_end:
            try:
                dt_end = to_datetime(dt_end, 23, 59)
            except ValueError as ve:
                raise BadRequest("Parameter 'to': {m}".format(m=ve.message))

        results, size = service.search_events_by_date(dt_start, start, count, dt_end=dt_end)
        return {'results': results, 'start': start, 'count': count, 'size': size}

    @accepts(JSON, HAL_JSON)
    def as_json(self, response):
        if issubclass(type(response), BaseResponse):
            # to handle 301 redirections and 404
            return response
        else:
            return HALEventsRepresentation(response['results'], request.url_rule.endpoint, response['start'],
                                       response['count'], response['size']).as_json()


class EventView(ServiceView):

    expires = timedelta(days=3)

    @cache.cached(timeout=600)
    def handle_request(self, ident):
        service = EventsService.from_context()
        event = service.get_event(ident)
        if event:
            return event
        else:
            raise NotFound()

    @accepts(JSON, HAL_JSON)
    def as_json(self, response):
        if issubclass(type(response), BaseResponse):
            # to handle 301 redirections and 404
            return response
        else:
            return HALEventRepresentation(response, request.url_rule.endpoint).as_json()


def to_datetime(dt, hour, minute):
    year, month, day = dt.split('-')
    return datetime(int(year), int(month), int(day), hour=hour, minute=minute)