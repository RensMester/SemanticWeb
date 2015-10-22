from app import app
import pprint  # noqa
from flask import render_template, request, jsonify  # noqa
import math  # noqa
import json  # noqa
from app import helper
from app import route_json  # noqa
from app import query


@app.route('/', )
def home():
    return render_template('index.html')


@app.route('/route', methods=['GET'])
def route():
    r = 0.07 / 111
    args = request.args
    route_start = args.get('start')
    route_dest = args.get('dest')

    upper_bound, lower_bound, steps = query.get_maps_route(route_start,
                                                           route_dest)
    places = query.get_places_within(upper_bound, lower_bound)
    places.extend(query.get_factforge())
    scenic = False
    if steps:
        while not scenic:
            if r > 0.1:
                break
            interesting, step_points = helper.get_in_area(steps, places, r)
            uri = query.insert_route(interesting)
            scenic = query.is_scenic(uri)
            print(scenic)
            r = r + 0.03
            scenic = True

    if scenic:
        route = helper.calculate_scenic_route(interesting, steps)
    else:
        route = helper.calculate_scenic_route(interesting, steps)

    return render_template('map.html', scenic=scenic, on_route=route,
                           step_points=step_points)
