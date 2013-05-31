from moxie.core.service import Service
from moxie.core.search import searcher, SearchServerException
from moxie.core.exceptions import ApplicationException

from .domain import Event


class EventsService(Service):

    def get_events_for_day(self, dt):
        """Get events starting the given day (between 00:00 and 23:59)
        :param dt: datetime of the given day (used for day, month, year only)
        :return: list of Event domain objects (empty list if no results)
        """
        start = dt.replace(hour=0, minute=0, second=0)
        end = dt.replace(hour=23, minute=59, second=59)
        q = {'q': 'event_start:[{start} TO {end}]'.format(start=Event._date_to_solr(start), end=Event._date_to_solr(end))}
        try:
            results = searcher.search(q)
        except SearchServerException:
            raise ApplicationException()
        return [Event.from_solr_dict(e) for e in results.results]

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