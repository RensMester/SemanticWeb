from flask import Flask

app = Flask(__name__)
app.config['maps_API_KEY'] = 'AIzaSyAFxFgbANCIn7i6Wpwve3_DXeOc-teeUvI'
app.config['maps_base_url'] = 'https://maps.googleapis.com/maps/api/directions/json?'
app.config['circle_radius'] = float(0.25 / 111)
app.config['endpoint'] = 'http://localhost:5820/ScenicRoute/query'
app.config['reasoning'] = 'true'
from app import views  # noqa
