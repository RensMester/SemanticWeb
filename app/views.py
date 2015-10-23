from app import app
import pprint  # noqa
from flask import render_template, request, jsonify, url_for  # noqa
import math  # noqa
import json  # noqa
from app import helper
from app import route_json  # noqa
from app import query


@app.route('/', methods=['GET'])
def home():
    return render_template('map.html')


@app.route('/route', methods=['POST', 'GET'])
def route():
    r = 0.07 / 111
    print(request.data)
    print(request.form)
    args = request.form
    route_start = args.get('start')
    route_dest = args.get('dest')

    upper_bound, lower_bound, steps = query.get_maps_route(route_start,
                                                           route_dest)
    places = query.get_places_within(upper_bound, lower_bound)
    places.extend(query.get_dbpedia())
    if steps:
        interesting, step_points = helper.get_in_area(steps, places, r)

    route, distance = helper.calculate_scenic_route(interesting, steps)
    return jsonify({'route': route, 'step_points': step_points,
                        'scenic_distance': distance})
