import requests
from pprint import pprint
import os
from dotenv import load_dotenv
load_dotenv()
api_keys = os.getenv("API_KEY")
location_api = requests.get(
    url="http://dataservice.accuweather.com/locations/v1/cities/geoposition/search",
    params={
        'apikey': api_keys,
        'q': '55.768760,37.588817',
        'language': 'ru-ru'

    }
 
)
location_key = location_api.json()["Key"]

hour1_forecast_api = requests.get(
    url=f"http://dataservice.accuweather.com/forecasts/v1/hourly/1hour/{location_key}",
    params={
        'apikey': api_keys,
        "language": 'ru-ru',
        'metric': 'true',
        'details': 'true'
    }
)
temperature = hour1_forecast_api.json()[0]['Temperature']['Value']


humidity = hour1_forecast_api.json()[0]["RelativeHumidity"]

wind_spead = hour1_forecast_api.json()[0]['Wind']['Speed']['Value']
rain_probailiti = hour1_forecast_api.json()[0]["RainProbability"]
print(f'температура: {temperature} {hour1_forecast_api.json()[0]['Temperature']['Unit']}\nвлажность: {humidity} %\nскорость ветра: {wind_spead} {hour1_forecast_api.json()[0]['Wind']['Speed']['Unit']},\nвероятность дождя: {rain_probailiti} %')
# pprint(hour1_forecast_api.json())

