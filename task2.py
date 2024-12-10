import requests
from pprint import pprint
import os
from dotenv import load_dotenv
load_dotenv()
api_keys = os.getenv("API_KEY")


def Location_key(latitude, longtude):
    location_api = requests.get(
        url="http://dataservice.accuweather.com/locations/v1/cities/geoposition/search",
        params={
            'apikey': api_keys,
            'q': f'{latitude},{longtude}',
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


# temperature = printWeather().json()[0]['Temperature']['Value'] # ТЕМПЕРАТУРА
# humidity = printWeather().json()[0]["RelativeHumidity"] # ВЛАЖНОСТЬ 
# wind_spead = printWeather().json()[0]['Wind']['Speed']['Value'] # скорость ВЕТРА 
# rain_probailiti = printWeather().json()[0]["RainProbability"] # Вероятность выпадения дождя
# PrecipitationProbability = printWeather().json()[0]["PrecipitationProbability"] # вероятность выпадения осадков
# HasPrecipitation = printWeather().json()[0]["HasPrecipitation"]# есть ли осадки в данный момент
# ThunderstormProbability = printWeather().json()[0]["ThunderstormProbability"] # Вероятность грозы
# метки плохой погоды
# print(f'температура: {temperature} {printWeather().json()[0]['Temperature']['Unit']}\nвлажность: {humidity} %\nскорость ветра: {wind_spead} {printWeather().json()[0]['Wind']['Speed']['Unit']},\nвероятность дождя: {rain_probailiti} %')
# pprint(printWeather().json())

def check_bad_weather():
    try:
      
        latitude = float(input('ВВедите широту: '))

        longtude = float(input('ВВедите долготу:'))
        loc_key = Location_key(latitude, longtude)
    except ValueError:
        print("Произошла ошибка с функцией")
    temperature = printWeather(loc_key).json()[0]['Temperature']['Value']
    wind_spead = printWeather(loc_key).json()[0]['Wind']['Speed']['Value']
    PrecipitationProbability = printWeather(loc_key).json()[0]["PrecipitationProbability"]
    HasPrecipitation = printWeather(loc_key).json()[0]["HasPrecipitation"]
    humidity = printWeather(loc_key).json()[0]["RelativeHumidity"]
    if (temperature <= 57 and temperature >= -90) and wind_spead < 20 and (PrecipitationProbability < 80) and humidity > 10 and humidity < 80:
        if temperature > 3 and temperature < 25 and wind_spead < 6 and PrecipitationProbability < 20 and humidity > 40 and humidity < 70 and HasPrecipitation == False:
            print("Погода приятная, можно гулять")
        else:
            print("Лучше прогулку отложить")
    else:
        print("Сегодня нельзя идти на прогулку, на улице очень опасно")
    

 
def FoundCity(nameCity):
    for_found_city = requests.get(
        url = "http://dataservice.accuweather.com/locations/v1/cities/search",
        params={
            'apikey': api_keys,
            'q': nameCity,
            'language': "ru-ru",
            'details': 'true'
        }
    )
    latitude = for_found_city.json()[0]['GeoPosition']['Latitude']
    longitude = for_found_city.json()[0]['GeoPosition']['longitude']
    return [latitude, longitude]

# City = FoundCity('Москва')
# pprint(City.json())
print(FoundCity('Москва'))
# 55.768045, 37.585129