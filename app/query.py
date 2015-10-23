from SPARQLWrapper import SPARQLWrapper, RDF, JSON  # noqa
import requests  # noqa
from app import app


def get_places_within(upper, lower):
    sparql = SPARQLWrapper(app.config['endpoint'])
    sparql.setReturnFormat(JSON)
    sparql.addParameter('Accept', 'application/sparql-results+json')
    sparql.addParameter('reasoning', 'true')
    prefixes = '''
            prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            prefix owl: <http://www.w3.org/2002/07/owl#>
            prefix xsd: <http://www.w3.org/2001/XMLSchema#>
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            '''
    query = '''
        select ?place ?lat ?lon where {
               ?place a scr:Place .
               ?place geo:lat ?lat .
               ?place geo:long ?lon .
               FILTER(xsd:float(?lat) < %f &&
                      xsd:float(?lon) < %f &&
                      xsd:float(?lat) > %f &&
                      xsd:float(?lon) > %f )
               }
            '''

    sparql.setQuery(prefixes + query % (upper[0], upper[1], lower[0], lower[1]))  # noqa

    response = sparql.query().convert()
    if response['results']['bindings']:
        return response['results']['bindings']
    else:
        return []


def get_dbpedia():
    print('getting dbpedia objects')
    url = 'http://dbpedia.org/sparql'
    headers = {'Accept': 'application/sparql-results+json', 'Content-Type':
               'application/x-www-form-urlencoded; charset=UTF-8', }

    prefixes = '''
                PREFIX dbc: <http://dbpedia.org/resource/Category:>
                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
                '''
    query = '''
            SELECT ?uri
            WHERE {
            ?x ?y dbc:%s .
            ?x owl:sameAs ?uri.
            FILTER(regex(?uri, "wikidata.dbpedia"))
            }
            '''
    DB_objects = ['Parks_in_Amsterdam', 'Squares_in_Amsterdam',
                  'Museums_in_Amsterdam']

    results = []
    results2 = []
    for object in DB_objects:
        new_query = prefixes + query % (object)
        response = requests.post(url, headers=headers, data={'query':
                                                             new_query}).json()
        if response['results']['bindings']:
            results.extend(response['results']['bindings'])

    url = 'http://wikidata.dbpedia.org/sparql'

    query = '''
            SELECT ?lat ?lon WHERE {
            <%s> geo:lat ?lat ;
            geo:long ?lon .
            }
            '''

    for place in results:
        new_query = prefixes + query % (place['uri']['value'])
        response = requests.post(url, headers=headers, data={'query':
                                                             new_query}).json()
        if response['results']['bindings']:
            bindings = response['results']['bindings']
            if bindings[0].get('lat'):
                bindings[0]['place'] = {'value': place['uri']['value']}
                results2.extend(bindings)
    print('got ', len(results2), ' objects')
    return results2


def get_maps_route(start, dest, travel='walking'):
    payload = {'origin': start,
               'destination': dest,
               'key': app.config['maps_API_KEY'],
               'mode': travel,
               }

    shortest_route = requests.get(app.config['maps_base_url'],
                                  params=payload).json()
    try:
        bounds = shortest_route['routes'][0]['bounds']
        upper_bound = bounds['northeast']['lat'], bounds['northeast']['lng']
        lower_bound = bounds['southwest']['lat'], bounds['southwest']['lng']
        steps = shortest_route['routes'][0]['legs'][0]['steps']
        return upper_bound, lower_bound, steps
    except Exception as e:
        print(e)
        return False


def insert_route(waypoints):
    sparql = SPARQLWrapper(app.config['endpoint'])
    sparql.setReturnFormat(JSON)
    existing_query = 'select ?uri where { ?uri a scr:Route .  } order by asc (?uri)'

    sparql.setQuery(existing_query)
    response = sparql.query().convert()
    number = 0
    start = waypoints.pop(0)
    destination = waypoints.pop(-1)

    if response['results']['bindings']:
        last = response['results']['bindings'][-1]
        print(last)
        print(int(last['uri']['value'][-1]) + 1)
        number = int(last['uri']['value'][-1]) + 1

    query = '''
        insert data{
        scr:Start%d a scr:Start;
                geo:lat %s;
                geo:long %s.
        scr:Destination%d a scr:Destination;
                geo:lat %s;
                geo:long %s.
            scr:Route%d a scr:Route ;
                scr:hasStart scr:Start%d;
                scr:hasDestination scr:Destination%d.
            ''' % (number, start['lat']['value'], start['lon']['value'],
                   number, destination['lat']['value'],
                   destination['lon']['value'], number, number, number)

    for uri in waypoints:
        query = query + 'scr:Route%d scr:hasPlace <' % (number) + \
            uri['place']['value'] + '/>. \n'

    query = query + '}'
    sparql.setQuery(query)
    sparql.query()
    return 'scr:Route%d' % (number)


def is_scenic(uri):
    sparql = SPARQLWrapper(app.config['endpoint'])
    sparql.addParameter('Accept', 'application/sparql-results+json')
    sparql.addParameter('reasoning', 'true')
    query = 'ask where {%s a scr:ScenicRoute}' % (uri)
    sparql.setQuery(query)
    response = sparql.query().convert()
    answer = response.getElementsByTagName('boolean')[0].childNodes[0].wholeText
    if answer == 'true':
        return True
    else:
        return False
