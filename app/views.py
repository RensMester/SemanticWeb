from app import app
import pprint
from flask import render_template, request, jsonify
from SPARQLWrapper import SPARQLWrapper, RDF, JSON
import requests
import math
import json
from route import *


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
    shortest_route = route

    pprint.pprint(shortest_route)
    sparql = SPARQLWrapper(app.config['endpoint'])
    query = 'select ?place ?lat ?lon where { ?place a scr:Place .' +\
        '?place geo:lat ?lat . ?place geo:long ?lon . }'

    sparql.setQuery(query)
    sparql.setReturnFormat(RDF)
    sparql.addParameter('Accept', 'application/sparql-results+json')
    sparql.addParameter('reasoning', 'true')

    response = sparql.query().convert()
    def in_circle(center_x, center_y, radius, x, y):
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
            if distance > 250:
                num_circles = int(distance / 200)
    return jsonify(shortest_route)

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
