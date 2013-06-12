from datetime import datetime, timedelta

from flask import request

from moxie.core.views import ServiceView, accepts
from moxie.core.cache import cache, args_cache_key
from moxie.core.exceptions import abort
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
            return abort(400, "'from' parameter is mandatory (e.g. 2012-12-12)")

        if dt_start == "now":
            dt_start = datetime.now()
        else:
            try:
                dt_start = to_datetime(dt_start)
            except ValueError as ve:
                return abort(400, 'from: {m}'.format(m=ve.message))

        if dt_end:
            try:
                dt_end = to_datetime(dt_end)
            except ValueError as ve:
                return abort(400, 'to: {m}'.format(m=ve.message))

        results, size = service.search_events_by_date(dt_start, start, count, dt_end=dt_end)
        return {'results': results, 'start': start, 'count': count, 'size': size}

    @accepts(JSON, HAL_JSON)
    def as_json(self, response):
        return HALEventsRepresentation(response['results'], request.url_rule.endpoint, response['start'],
                                       response['count'], response['size']).as_json()


class EventsToday(ServiceView):

    expires = datetime.utcnow().replace(hour=23, minute=59, second=59)

    @cache.cached(timeout=600)
    def handle_request(self):
        service = EventsService.from_context()
        start = request.args.get('start', 0)
        count = request.args.get('count', 35)
        results, size = service.get_events_for_day(datetime.today(), start, count)
        return {'results': results, 'start': start, 'count': count, 'size': size}

    @accepts(JSON, HAL_JSON)
    def as_json(self, response):
        return HALEventsRepresentation(response['results'], request.url_rule.endpoint, response['start'],
                                       response['count'], response['size']).as_json()


class EventsForDate(ServiceView):

    @cache.cached(timeout=600)
    def handle_request(self, year, month, day):
        service = EventsService.from_context()
        start = request.args.get('start', 0)
        count = request.args.get('count', 35)
        try:
            date = datetime(int(year), int(month), int(day))
        except ValueError as ve:
            return abort(400, ve.message)
        else:
            results, size = service.get_events_for_day(date, start, count)
            return {'results': results, 'start': start, 'count': count, 'size': size,
                    'year': year, 'month': month, 'day': day}

    @accepts(JSON, HAL_JSON)
    def as_json(self, response):
        if issubclass(type(response), BaseResponse):
            return response
        else:
            return HALEventsRepresentation(response['results'], request.url_rule.endpoint, response['start'],
                                           response['count'], response['size'], day=response['day'],
                                           month=response['month'], year=response['year']).as_json()


class EventView(ServiceView):

    expires = timedelta(days=3)

    @cache.cached(timeout=600)
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


def to_datetime(dt):
    year, month, day = dt.split('-')
    return datetime(int(year), int(month), int(day))