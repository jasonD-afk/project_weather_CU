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

def check_bad_weather(loc_key):
    weather_info = printWeather(loc_key).json()[0]
    temperature = weather_info['Temperature']['Value']
    wind_speed = weather_info['Wind']['Speed']['Value']
    PrecipitationProbability = weather_info["PrecipitationProbability"]
    HasPrecipitation = weather_info["HasPrecipitation"]
    humidity = weather_info["RelativeHumidity"]
    if (temperature <= 57 and temperature >= -90) and wind_speed < 70 and (PrecipitationProbability < 80) and humidity > 10 and humidity < 90:
        if temperature > 3 and temperature < 25 and wind_speed < 20 and PrecipitationProbability < 35 and humidity > 20 and humidity < 85 and HasPrecipitation == False:
            return("Погода приятная, можно гулять")
        else:
            return ("Лучше прогулку отложить")
    else:
        return("Сегодня нельзя идти на прогулку, на улице очень опасно")

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
    
@app.route('/advice', methods=['GET', "POST"])
def advice_point():
    if request.method == 'GET':
        return render_template('advice.html')
    try:
        latitude = request.form.get('latitude', type=float)
        longitude = request.form.get('longitude', type=float)

        if latitude is None or longitude is None:
            return render_template('advice.html', error="Invalid input")

        loc_key = Location_key(latitude, longitude)

        check_weather = check_bad_weather(loc_key)
        
        return render_template('result_bad_weather.html', check_weather=check_weather)    
    except ValueError:
        return render_template('advice.html', error="Invalid coordinates format")
    except Exception as e:
        return render_template('advice.html', error=str(e))

   


if __name__ == "__main__":
    app.run(debug=True)