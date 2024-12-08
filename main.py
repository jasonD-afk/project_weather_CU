import requests
from pprint import pprint

response = requests.get(
    url="http://dataservice.accuweather.com/locations/v1/cities/geoposition/search",
    params={
        'apikey': "VWOEIIGDxX7dgDf1WvVKzsA5gsAw6qGy",
        'q': '55.768760,37.588817',
        'language': 'ru-ru'

    }

)
pprint(response.json())