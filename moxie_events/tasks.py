import logging

from moxie import create_app
from moxie.core.search import searcher
from moxie.worker import celery
from moxie_events.importers.talks_cam import TalksCamEventsImporter

logger = logging.getLogger(__name__)
BLUEPRINT_NAME = 'events'


@celery.task
def import_ox_talks(force_update=False):
    app = create_app()
    with app.blueprint_context(BLUEPRINT_NAME):
        importer = TalksCamEventsImporter(['http://talks.ox.ac.uk/show/xml/4563'], searcher)
        importer.run()
