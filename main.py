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
pprint(location_api.json())

