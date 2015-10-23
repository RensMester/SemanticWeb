from flask import Flask

app = Flask(__name__)
app.config['maps_API_KEY'] = ''
app.config['maps_base_url'] = 'https://maps.googleapis.com/maps/api/directions/json?'
app.config['endpoint'] = 'http://localhost:5820/scenicroute/query'
app.config['reasoning'] = 'true'
from app import views  # noqa
from app import helper  # noqa
from app import query  # noqa
from app import route_json  # noqa
