from flask import Flask, jsonify, request, render_template
import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_keys = os.getenv("API_KEY")

app = Flask(__name__)

def Location_key(latitude, longitude):
    location_api = requests.get(
        url="http://dataservice.accuweather.com/locations/v1/cities/geoposition/search",
        params={
            'apikey': api_keys,
            'q': f'{latitude},{longitude}',
            'language': 'ru-ru'
        }
    )
    location_key = location_api.json()["Key"]
    return location_key

def printWeather(loc_key):
    hour1_forecast_api = requests.get(
        url=f"http://dataservice.accuweather.com/forecasts/v1/hourly/1hour/{loc_key}",
        params={
            'apikey': api_keys,
            "language": 'ru-ru',
            'metric': 'true',
            'details': 'true'
        }
    )
    return hour1_forecast_api

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/weather', methods=['GET', 'POST'])
def get_weather():
    if request.method == 'GET':
        return render_template('weather.html')
    
    try:
        latitude = request.form.get('latitude', type=float)
        longitude = request.form.get('longitude', type=float)

        if latitude is None or longitude is None:
            return render_template('weather.html', error="Invalid input")

        loc_key = Location_key(latitude, longitude)

        weather_data = printWeather(loc_key).json()[0]

        response = {
            "temperature": f"{weather_data['Temperature']['Value']} {weather_data['Temperature']['Unit']}",
            "humidity": f"{weather_data['RelativeHumidity']} %",
            "wind_speed": f"{weather_data['Wind']['Speed']['Value']} {weather_data['Wind']['Speed']['Unit']}",
            "rain_probability": f"{weather_data['RainProbability']} %"
        }

        return render_template('result.html', **response)

    except ValueError:
        return render_template('weather.html', error="Invalid coordinates format")
    except Exception as e:
        return render_template('weather.html', error=str(e))

if __name__ == "__main__":
    app.run(debug=True)