import logging

from moxie import create_app
from moxie.core.search import searcher
from moxie.worker import celery
from moxie_events.importers.talks_cam import TalksCamEventsImporter

logger = logging.getLogger(__name__)
BLUEPRINT_NAME = 'events'

# FEEDS_URLS_KEY = 'NEW_TALKS_URLS'
FEEDS_URLS_KEY = 'NEW_TALKS_URLS'


@celery.task
def import_ox_talks(force_update=False):
    app = create_app()
    with app.blueprint_context(BLUEPRINT_NAME):
        if FEEDS_URLS_KEY in app.config:
            importer = TalksCamEventsImporter(app.config[FEEDS_URLS_KEY], searcher)
            importer.run()
        else:
            logger.warn("TalksCam provider not configured with {key} in config.".format(key=FEEDS_URLS_KEY))
