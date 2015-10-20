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
    route_start = args.get('start')
    route_dest = args.get('dest')

    upper_bound, lower_bound, steps = query.get_maps_route(route_start,
                                                           route_dest)
    places = query.get_places_within(upper_bound, lower_bound)

    step_points = []
    if steps:
        start_latlon = steps[0]['start_location']['lat'],steps[0]['start_location']['lng']
        interesting = [{'lat': {'value': str(start_latlon[0])},
                        'lon': {'value': str(start_latlon[1])}}]

        for step in steps:
            start, end = step['start_location'], step['end_location']
            start_latlon = start['lat'], start['lng']
            end_latlon = end['lat'], end['lng']

            distance = step['distance']['value']
            if distance > 200:
                num_circles = int(distance / 200)
                print('############################')
                print(num_circles)
                for i in range(0, num_circles + 1):
                    #    print(i/(num_circles + 1))
                    lat, lon = helper.step_point(start_latlon, end_latlon,
                                                 i/(num_circles + 1))
                    in_circle = [p for p in places
                                 if helper.in_circle(lat, lon, r,
                                                     p['lat']['value'],
                                                     p['lon']['value'])]
                    step_points.append((lat, lon))
                    in_circle = list(in_circle)
                    print(len(in_circle))
                    if len(in_circle) > 5:
                        random.shuffle(in_circle)

                    interesting.extend(in_circle[:1])
                print('############################')
        interesting.append({'lat': {'value': str(end_latlon[0])},
                            'lon': {'value': str(end_latlon[1])}})

    print(interesting)
    route = []
    uri = query.insert_route(interesting)
    scenic = query.is_scenic(uri)

    for i, p in enumerate(interesting):
        lat, lon = p['lat']['value'], p['lon']['value']
        if i == len(interesting) - 1:
            pass

        else:
            n_lat, n_lon = interesting[i+1]['lat']['value'], interesting[i+1]['lon']['value']
            route.extend(helper.route((lat, lon), (n_lat, n_lon)))
    # end_latlon = steps[-1]['end_location']['lat'], steps[-1]['end_location']['lng']
    # route.extend(helper.route((lat, lon), end_latlon))

    return render_template('map.html', on_route=route, step_points=step_points)
