from moxie.core.service import Service
from moxie.core.search import searcher, SearchServerException
from moxie.core.exceptions import ApplicationException

from .domain import Event


class EventsService(Service):

    def get_events_for_day(self, dt, start, count):
        """Get events starting the given day (between 00:00 and 23:59)
        :param dt: datetime of the given day (used for day, month, year only)
        :param start: first result to retrieve
        :param count: number of results to retrieve
        :return: list of Event domain objects (empty list if no results)
        """
        dt_start = dt.replace(hour=0, minute=0, second=0)
        return self.search_events_by_date(dt_start, start, count)

    def search_events_by_date(self, dt_start, start, count, dt_end=None):
        """Search events by date
        :param dt_start: datetime object
        :param start: first result to retrieve
        :param count: number of results to retrieve
        :param dt_end: (optional) datetime object - limit the end result
        :return: list of Event domain objects (empty list if no results)
        """
        if dt_end:
            q = {'q': 'event_start:[{start} TO {end}]'.format(start=Event._date_to_solr(dt_start),
                                                          end=Event._date_to_solr(dt_end))}
        else:
            q = {'q': 'event_start:[{start} TO *]'.format(start=Event._date_to_solr(dt_start))}

        q['sort'] = "event_start asc"

        try:
            results = searcher.search(q, start=start, count=count)
        except SearchServerException:
            raise ApplicationException()
        return [Event.from_solr_dict(e) for e in results.results], results.size

    def get_event(self, uid):
        """Get an event by its unique identifier
        :param uid: identifier of the event
        :return: Event domain object or None if not found
        """
        docs = searcher.get_by_ids([uid])
        if docs.results:
            return Event.from_solr_dict(docs.results[0])
        else:
            return None