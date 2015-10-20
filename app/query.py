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


def get_factforge():
	sparql = SPARQLWrapper('http://factforge.net/sparql')
	sparql.setReturnFormat(JSON)
	sparql.addParameter('Accept', 'application/sparql-results+json')
	sparql.addParameter('reasoning', 'true')

	prefixes = '''PREFIX geo-pos: <http://www.w3.org/2003/01/geo/wgs84_pos#>
		PREFIX omgeo: <http://www.ontotext.com/owlim/geo#>
		PREFIX dbpedia: <http://dbpedia.org/resource/>
		PREFIX gn: <http://www.geonames.org/ontology#>

	'''
	query = '''
	SELECT distinct ?place ?label ?lat ?lon
	WHERE {
		dbpedia:Amsterdam geo-pos:lat ?latBase ;
				   geo-pos:long ?longBase .
		?place omgeo:nearby(?latBase ?longBase "5km");
					gn:featureCode gn:%s ;
					geo-pos:lat ?lat ;
			geo-pos:long ?lon ;
			gn:name ?label . 

	}
	'''

	FF_objects = ['L.PRK', 'S.CH', 'S.MLWND', 'S.MKT', 'S.MUS', 'S.PAL', 'S.SQR', 'S.MNMT']

	for object in FF_objects:
		new_query = prefixes + query % (object)
		sparql.setQuery(new_query)
		print(sparql.query().convert())

def get_maps_route(start, dest):
    payload = {'origin': start,
               'destination': dest,
               'key': app.config['maps_API_KEY'],
               'mode': 'walking',
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
    sparql.addParameter('Accept', 'application/sparql-results+json')
    sparql.addParameter('reasoning', 'true')
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
        scr:Start1 a scr:Start;
                geo:lat %s;
                geo:long %s.
        scr:Destination1 a scr:Destination;
                geo:lat %s;
                geo:long %s.
            scr:Route%d a scr:Route ;
                scr:hasStart scr:Start1;
                scr:hasDestination scr:Destination1.
            ''' % (start['lat']['value'], start['lon']['value'],
                   destination['lat']['value'], destination['lon']['value'],
                   number)

    for uri in waypoints:
        query = query + 'scr:Route0 scr:hasPlace <' + uri['place']['value'] + '/>. \n'

    query = query + '}'
    print(query)
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
