from app import app
import pprint
from flask import render_template, request, jsonify
from SPARQLWrapper import SPARQLWrapper, RDF, JSON
import requests
import math
import json
from app import helper
from app import route_json

prefixes = 'prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>' +\
           'prefix owl: <http://www.w3.org/2002/07/owl#>' +\
           'prefix xsd: <http://www.w3.org/2001/XMLSchema#>' +\
           'prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>'
r = 0.1 / 111


@app.route('/', )
def home():
    return render_template('index.html')


@app.route('/route', methods=['GET'])
def sparql():
    args = request.args
    start = args.get('start')
    dest = args.get('dest')
    waypoints = []

    payload = {'origin': start,
               'destination': dest,
               'waypoints': 'optimize:true|' + '|'.join(waypoints),
               'key': app.config['maps_API_KEY'],
               'mode': 'walking',
               }

    # shortest_route = requests.get(app.config['maps_base_url'],
    #                               params=payload).json()
    shortest_route = route_json.route

    sparql = SPARQLWrapper(app.config['endpoint'])

    query = 'select ?place ?lat ?lon where { ?place a scr:Place .' +\
        '?place geo:lat ?lat . ?place geo:long ?lon . }'

    sparql.setQuery(prefixes + query)
    sparql.setReturnFormat(JSON)
    sparql.addParameter('Accept', 'application/sparql-results+json')
    sparql.addParameter('reasoning', 'true')

    response = sparql.query().convert()
    if response['results']['bindings']:
        objs = response['results']['bindings']

    def in_circle(center_x, center_y, radius, x, y):
        center_x, center_y, x, y = map(float, (center_x, center_y, x, y))
        square_dist = (center_x - x) ** 2 + (center_y - y) ** 2
        return square_dist <= radius ** 2

    circles = []

    if shortest_route:
        steps = shortest_route['routes'][0]['legs'][0]['steps']
        for step in steps:
            start = step['start_location']
            end = step['end_location']
            start_lat, start_lon = start['lat'], start['lng']
            end_lat, end_lon = end['lat'], end['lng']

            distance = step['distance']['value']
            if distance > 150:
                num_circles = int(distance / 100)
                print('############################')
                print(num_circles)
                for i in range(0, num_circles + 1):
                    print(i/(num_circles+1))
                    lat, lon = helper.intermediate_point((start_lat, start_lon), (end_lat, end_lon), i/(num_circles + 1))
                    circles.append({'lat': lat, 'lon': lon})
                print('############################')

    on_route = [obj for c in circles for obj in objs if
                in_circle(c['lat'], c['lon'], r, obj['lat']['value'],
                          obj['lon']['value'])]

    print(len(on_route))
    print(len(circles))

    return render_template('map.html', route=steps, circles=circles, )

    """
    if endpoint and query :
        sparql = SPARQLWrapper(endpoint)

        sparql.setQuery(query)

        if return_format == 'RDF':
            sparql.setReturnFormat(RDF)
        else :
            sparql.setReturnFormat(JSON)
            sparql.addParameter('Accept','application/sparql-results+json')

        sparql.addParameter('reasoning','true')

        app.logger.debug('Query:\n{}'.format(query))

        app.logger.debug('Querying endpoint {}'.format(endpoint))

        try :
            response = sparql.query().convert()

            app.logger.debug('Results were returned, yay!')

            app.logger.debug(response)

            if return_format == 'RDF':
                app.logger.debug('Serializing to Turtle format')
                return response.serialize(format='nt')
            else :
                app.logger.debug('Directly returning JSON format')
                return jsonify(response)
        except Exception as e:
            app.logger.error('Something went wrong')
            app.logger.error(e)
            return jsonify({'result': 'Error'})


    else :
        return jsonify({'result': 'Error'})
    """
