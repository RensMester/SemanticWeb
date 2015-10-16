from app import app
import pprint  # noqa
from flask import render_template, request, jsonify  # noqa
import math  # noqa
import json  # noqa
from app import helper
from app import route_json  # noqa
from app import query
import random

r = 0.1 / 111


@app.route('/', )
def home():
    return render_template('index.html')


@app.route('/route', methods=['GET'])
def route():
    args = request.args
    start = args.get('start')
    dest = args.get('dest')

    interesting = []
    upper_bound, lower_bound, steps = query.get_maps_route(start, dest)
    places = query.get_places_within(upper_bound, lower_bound)

    if steps:
        for step in steps:
            start, end = step['start_location'], step['end_location']
            start_latlon = start['lat'], start['lng']
            end_latlon = end['lat'], end['lng']

            distance = step['distance']['value']
            if distance > 150:
                num_circles = int(distance / 100)
                print('############################')
                print(num_circles)
                for i in range(0, num_circles + 1):
                    lat, lon = helper.step_point(start_latlon, end_latlon,
                                                 i/(num_circles + 1))
                    in_circle = [place for place in places if
                                 helper.in_circle(lat, lon, r, place['lat']['value'],
                                                  place['lon']['value'])]
                    if len(in_circle) > 5:
                        random.shuffle(in_circle)

                    interesting.extend(in_circle[:1])
                print('############################')
    route = []

    for i, p in enumerate(interesting):
        lat, lon = p['lat']['value'], p['lon']['value']
        if i == len(interesting) - 1:
            pass
        else:
            n_lat, n_lon = interesting[i+1]['lat']['value'], interesting[i+1]['lon']['value']
            route.extend(helper.route((lat, lon), (n_lat, n_lon)))

    return render_template('map.html', on_route=route,)
