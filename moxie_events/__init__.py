from flask import Blueprint, request, make_response

from moxie.core.representations import HALRepresentation

from .views import EventView, EventsSearch


def create_blueprint(blueprint_name, conf):
    events_blueprint = Blueprint(blueprint_name, __name__, **conf)

    events_blueprint.add_url_rule('/', view_func=get_routes)

    events_blueprint.add_url_rule('/search', view_func=EventsSearch.as_view('search'))

    events_blueprint.add_url_rule('/<ident>', view_func=EventView.as_view('event'))

    return events_blueprint


def get_routes():
    path = request.path
    representation = HALRepresentation({})
    representation.add_curie('hl', 'http://moxie.readthedocs.org/en/latest/http_api/events.html#{rel}')
    representation.add_link('self', '{bp}'.format(bp=path))
    representation.add_link('hl:search', '{bp}search'.format(bp=path),
                            title="Search events")
    representation.add_link('hl:event', '{bp}event/{{id}}'.format(bp=path),
                            templated=True, title="Event")
    response = make_response(representation.as_json(), 200)
    response.headers['Content-Type'] = "application/json"
    return response