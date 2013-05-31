from flask import Blueprint, request, make_response

from moxie.core.representations import HALRepresentation

from .views import EventsToday, EventsForDate, EventView


def create_blueprint(blueprint_name, conf):
    events_blueprint = Blueprint(blueprint_name, __name__, **conf)

    events_blueprint.add_url_rule('/', view_func=get_routes)

    events_blueprint.add_url_rule('/today', view_func=EventsToday.as_view('today'))

    events_blueprint.add_url_rule('/<year>-<month>-<day>', view_func=EventsForDate.as_view('day'))

    events_blueprint.add_url_rule('/event/<ident>', view_func=EventView.as_view('event'))

    return events_blueprint


def get_routes():
    path = request.path
    representation = HALRepresentation({})
    representation.add_curie('hl', 'http://moxie.readthedocs.org/en/latest/http_api/events.html#{rel}')
    representation.add_link('self', '{bp}'.format(bp=path))
    representation.add_link('hl:today', '{bp}today'.format(bp=path),
                            title='Today events')
    representation.add_link('hl:date', '{bp}{{yyyy}}-{{mm}}-{{dd}}'.format(bp=path),
                            templated=True, title="Events for given date")
    response = make_response(representation.as_json(), 200)
    response.headers['Content-Type'] = "application/json"
    return response