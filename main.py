from flask import Flask, jsonify, request, render_template, session, redirect
import requests
import os
from dotenv import load_dotenv

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd

import dash_leaflet as dl
import openrouteservice

load_dotenv()
api_keys = os.getenv("API_KEY")  # AccuWeather API Key
ors_api_key = "5b3ce3597851110001cf624873e06e7cf4c74f5a934bad1b5b9c73e2"  # OpenRouteService API Key

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Замените на ваш секретный ключ

# Инициализируем Dash внутри Flask
dash_app = dash.Dash(
    __name__,
    server=app,
    url_base_pathname='/dash/',
    suppress_callback_exceptions=True
)
dash_app.title = 'Weather Visualization'


def Location_key(latitude, longitude):
    try:
        location_api = requests.get(
            url="http://dataservice.accuweather.com/locations/v1/cities/geoposition/search",
            params={
                'apikey': api_keys,
                'q': f'{latitude},{longitude}',
                'language': 'ru-ru'
            }
        )
        location_api.raise_for_status()
        location_key = location_api.json()["Key"]
        return location_key
    except Exception as e:
        print(f"Ошибка при получении Location Key: {e}")
        return None

def get_forecast_data(loc_key):
    try:
        forecast_api = requests.get(
            url=f"http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{loc_key}",
            params={
                'apikey': api_keys,
                "language": 'ru-ru',
                'metric': 'true',
                'details': 'true'
            }
        )
        forecast_api.raise_for_status()
        data = forecast_api.json()
        for item in data:
            item['DateTime'] = pd.to_datetime(item['DateTime'])
        return data
    except Exception as e:
        print(f"Ошибка при получении прогноза погоды: {e}")
        return None


def printWeather(loc_key):
    try:
        hour1_forecast_api = requests.get(
            url=f"http://dataservice.accuweather.com/forecasts/v1/hourly/1hour/{loc_key}",
            params={
                'apikey': api_keys,
                "language": 'ru-ru',
                'metric': 'true',
                'details': 'true'
            }
        )
        hour1_forecast_api.raise_for_status()
        return hour1_forecast_api
    except Exception as e:
        print(f"Ошибка при получении текущего прогноза погоды: {e}")
        return None


def get_daily_forecast_data(loc_key, days):
    try:
        if days == 1:
            url = f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{loc_key}"
        elif days in [3, 5]:
            url = f"http://dataservice.accuweather.com/forecasts/v1/daily/5day/{loc_key}"
        else:
            return None  # Неподдерживаемый интервал

        forecast_api = requests.get(
            url=url,
            params={
                'apikey': api_keys,
                'language': 'ru-ru',
                'metric': 'true',
                'details': 'true'  # Добавляем детали
            }
        )
        forecast_api.raise_for_status()
        data = forecast_api.json()
        if days == 3:
            data['DailyForecasts'] = data['DailyForecasts'][:3]
        return data['DailyForecasts']
    except Exception as e:
        print(f"Ошибка при получении прогноза на несколько дней: {e}")
        return None

def check_bad_weather(loc_key):
    weather_info = get_forecast_data(loc_key)
    if weather_info:
        weather_info = weather_info[0]
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
    else:
        return "Невозможно получить данные о погоде."

def FoundCity(nameCity):
    try:
        for_found_city = requests.get(
            url = "http://dataservice.accuweather.com/locations/v1/cities/search",
            params={
                'apikey': api_keys,
                'q': nameCity,
                'language': "ru-ru",
                'details': 'true'
            }
        )
        for_found_city.raise_for_status()
        city_data = for_found_city.json()[0]
        Latitude = city_data['GeoPosition']['Latitude']
        Longitude = city_data['GeoPosition']['Longitude']
        City_name = city_data['LocalizedName']
        Country = city_data['Country']['LocalizedName']

        City_information = {'lat': Latitude, 'lon': Longitude, 'country': Country, 'city': City_name}
        return City_information
    except Exception as e:
        print(f"Ошибка при поиске города: {e}")
        return None

def get_route(coords):
    try:
        client = openrouteservice.Client(key=ors_api_key)
        routes = client.directions(coords, profile='driving-car')
        geometry = routes['routes'][0]['geometry']
        decoded = openrouteservice.convert.decode_polyline(geometry)
        route = [(coord[1], coord[0]) for coord in decoded['coordinates']]  # Меняем порядок на (lat, lng)
        return route
    except openrouteservice.exceptions.ApiError as api_err:
        print(f"API Error: {api_err}")
        print(f"Error Details: {api_err.args}")
        return None
    except Exception as e:
        print(f"Ошибка при получении маршрута: {e}")
        import traceback
        traceback.print_exc()
        return None


# Маршруты Flask

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
        weather_response = printWeather(loc_key)

        if weather_response is None:
            return render_template('weather.html', error="Не удалось получить данные о погоде.")

        weather_data = weather_response.json()[0]

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
        print(f"Ошибка: {e}")
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
    

@app.route('/from_city_to_city', methods=['GET', "POST"])
def search_city():
    if request.method == 'GET':
        return render_template('from_city_to_city.html')
    try:
        city_1 = request.form.get('city_1', type=str).strip()
        city_2 = request.form.get('city_2', type=str).strip()

        if not city_1 or not city_2:
            return render_template('from_city_to_city.html', error="Пожалуйста, введите оба города.")

        cities_data = []

        for city_name in [city_1, city_2]:
            try:
                city_inf = FoundCity(city_name)
                if not city_inf:
                    return render_template('from_city_to_city.html', error=f"Не удалось найти город {city_name}. Проверьте правильность ввода.")
            except IndexError:
                return render_template('from_city_to_city.html', error=f"Не удалось найти город {city_name}. Проверьте правильность ввода.")

            latitude = city_inf['lat']
            longitude = city_inf['lon']
            country = city_inf['country']
            city = city_inf['city']

            loc_key = Location_key(latitude, longitude)
            weather_response = printWeather(loc_key)

            if weather_response is None:
                return render_template('from_city_to_city.html', error=f"Не удалось получить данные о погоде для города {city_name}.")

            weather_data = weather_response.json()[0]
            check_weather = check_bad_weather(loc_key)

            data = {
                'city': city,
                'country': country,
                'temperature': f"{weather_data['Temperature']['Value']} {weather_data['Temperature']['Unit']}",
                'humidity': f"{weather_data['RelativeHumidity']} %",
                'wind_speed': f"{weather_data['Wind']['Speed']['Value']} {weather_data['Wind']['Speed']['Unit']}",
                'rain_probability': f"{weather_data['RainProbability']} %",
                'advice': check_weather,
                'lat': latitude,
                'lon': longitude
            }
            cities_data.append(data)

        # Сохраняем данные в сессии для использования в Dash
        session['city_data_list'] = cities_data

        return render_template('result_last.html', cities_data=cities_data)

    except ValueError:
        return render_template('from_city_to_city.html', error="Неверный формат ввода.")
    except Exception as e:
        print(f"Ошибка: {e}")
        return render_template('from_city_to_city.html', error=f"Произошла ошибка: {str(e)}")
    

# Новый маршрут для визуализации погоды
@app.route('/visualization', methods=['GET', 'POST'])
def visualization():
    if request.method == 'POST':
        # Получить данные из формы
        city_names = []
        num_locations = int(request.form.get('num_locations', 1))
        for i in range(1, num_locations + 1):
            city_name = request.form.get(f'city_{i}', type=str).strip()
            if not city_name:
                return render_template('visualization_form.html', error="Введите название города.")
            city_names.append(city_name)

        # Получить количество дней
        days = int(request.form.get('days', 1))

        # Получить информацию о каждом городе
        city_data_list = []
        for city_name in city_names:
            city_info = FoundCity(city_name)
            if city_info:
                city_data_list.append(city_info)
            else:
                return render_template('visualization_form.html', error=f"Город '{city_name}' не найден.")

        # Сохранить данные в сессии
        session['city_data_list'] = city_data_list
        # Перенаправить на страницу Dash с параметром days
        return redirect(f'/dash/?days={days}')
    return render_template('visualization_form.html')

# Макет Dash-приложения

dash_app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='city-data-store', storage_type='session'),
    html.H1('Визуализация погоды'),
    html.Div([
        html.Label('Выберите параметр для отображения:'),
        dcc.Dropdown(
            id='parameter-dropdown',
            options=[
                {'label': 'Максимальная температура', 'value': 'Temperature'},
                {'label': 'Минимальная температура', 'value': 'TemperatureMin'},
                {'label': 'Скорость ветра', 'value': 'WindSpeed'},
                {'label': 'Вероятность осадков', 'value': 'PrecipitationProbability'}
            ],
            value='Temperature',
            clearable=False
        )
    ]),
    html.Div([
        html.Label('Выберите тип графика:'),
        dcc.Dropdown(
            id='chart-type-dropdown',
            options=[
                {'label': 'Линейный график', 'value': 'line'},
                {'label': 'Столбчатая диаграмма', 'value': 'bar'}
            ],
            value='line',
            clearable=False
        )
    ]),
    html.Div([
        html.Label('Выберите временной интервал:'),
        dcc.RadioItems(
            id='days-radio',
            options=[
                {'label': '1 день', 'value': 1},
                {'label': '3 дня', 'value': 3},
                {'label': '5 дней', 'value': 5}
            ],
            value=1,  # Устанавливаем значение по умолчанию
            labelStyle={'display': 'inline-block', 'margin-right': '10px'}
        )
    ]),
    dcc.Graph(id='weather-graph'),
    html.H2('Маршрут на карте'),
    html.Div(id='map-container'),
    html.Div(id='hidden-div', style={'display': 'none'})
])

# Колбэк для обновления значения days-radio на основе параметра URL

from urllib.parse import parse_qs

@dash_app.callback(
    Output('days-radio', 'value'),
    Input('url', 'search')
)
def update_days_radio(search):
    if search:
        query = parse_qs(search.lstrip('?'))
        days_list = query.get('days', [1])
        try:
            days = int(days_list[0])
        except ValueError:
            days = 1
        return days
    else:
        return 1

# Колбэк для передачи данных из сессии в Dash
@dash_app.callback(
    Output('city-data-store', 'data'),
    Input('hidden-div', 'children')
)
def update_store(_):
    # Получаем данные из сессии Flask
    from flask import session
    city_data_list = session.get('city_data_list', [])
    return city_data_list

# Колбэк для обновления графика
@dash_app.callback(
    Output('weather-graph', 'figure'),
    [Input('parameter-dropdown', 'value'),
     Input('chart-type-dropdown', 'value'),
     Input('city-data-store', 'data'),
     Input('days-radio', 'value')]
)
def update_graph(selected_parameter, chart_type, city_data_list, days):
    if not city_data_list or not selected_parameter:
        return go.Figure()

    data_series = []

    for city_data in city_data_list:
        city_name = city_data['city']
        latitude = city_data['lat']
        longitude = city_data['lon']
        loc_key = Location_key(latitude, longitude)
        forecast_data = get_daily_forecast_data(loc_key, days)
        if not forecast_data:
            continue

        dates = [pd.to_datetime(item['Date']) for item in forecast_data]

        if selected_parameter == 'Temperature':
            values = [item['Temperature']['Maximum']['Value'] for item in forecast_data]
            unit = forecast_data[0]['Temperature']['Maximum']['Unit']
            yaxis_title = f'Макс. температура ({unit})'
        elif selected_parameter == 'TemperatureMin':
            values = [item['Temperature']['Minimum']['Value'] for item in forecast_data]
            unit = forecast_data[0]['Temperature']['Minimum']['Unit']
            yaxis_title = f'Мин. температура ({unit})'
        elif selected_parameter == 'WindSpeed':
            values = []
            for item in forecast_data:
                try:
                    wind_speed = item['Day']['Wind']['Speed']['Value']
                    values.append(wind_speed)
                except KeyError:
                    # Если данные отсутствуют, используем значение по умолчанию или пропускаем
                    values.append(None)
            unit = forecast_data[0]['Day']['Wind']['Speed'].get('Unit', '')
            yaxis_title = f'Скорость ветра ({unit})'
        elif selected_parameter == 'PrecipitationProbability':
            values = [item['Day'].get('PrecipitationProbability', 0) for item in forecast_data]
            yaxis_title = 'Вероятность осадков (%)'
        else:
            values = []
            yaxis_title = ''

        trace_name = f"{city_name}"

        if chart_type == 'line':
            trace = go.Scatter(
                x=dates,
                y=values,
                mode='lines+markers',
                name=trace_name,
                hoverinfo='x+y',
            )
        elif chart_type == 'bar':
            trace = go.Bar(
                x=dates,
                y=values,
                name=trace_name,
                hoverinfo='x+y',
            )
        else:
            trace = go.Scatter(
                x=dates,
                y=values,
                mode='lines+markers',
                name=trace_name,
                hoverinfo='x+y',
            )

        data_series.append(trace)

    layout = go.Layout(
        title=f'Прогноз погоды на {days} дней',
        xaxis=dict(title='Дата'),
        yaxis=dict(title=yaxis_title),
        hovermode='closest'
    )

    figure = go.Figure(data=data_series, layout=layout)

    return figure

# Колбэк для обновления карты
@dash_app.callback(
    Output('map-container', 'children'),
    Input('city-data-store', 'data')
)
def update_map(city_data_list):
    if not city_data_list or len(city_data_list) < 2:
        return html.P("Для отображения маршрута на карте необходимо указать как минимум два города.")

    # Получение координат городов
    coords = []
    markers = []
    for city_data in city_data_list:
        city_name = city_data['city']
        latitude = city_data['lat']
        longitude = city_data['lon']
        coords.append((longitude, latitude))  # Для OpenRouteService порядок (lng, lat)

        # Получаем прогноз погоды для города
        loc_key = Location_key(latitude, longitude)
        forecast_data = get_daily_forecast_data(loc_key, 1)
        if forecast_data:
            forecast_today = forecast_data[0]
            temperature = forecast_today['Temperature']['Maximum']['Value']
            unit = forecast_today['Temperature']['Maximum']['Unit']
            weather_text = forecast_today['Day']['IconPhrase']
        else:
            temperature = 'N/A'
            unit = ''
            weather_text = 'Нет данных'

        # Создаем маркер с информацией о погоде
        marker = dl.Marker(
            position=(latitude, longitude),
            children=[
                dl.Tooltip(city_name),
                dl.Popup([
                    html.H4(f"{city_name}"),
                    html.P(f"Температура: {temperature} {unit}"),
                    html.P(f"Погодные условия: {weather_text}")
                ])
            ]
        )
        markers.append(marker)

    # Получение маршрута
    route = get_route(coords)
    if not route:
        return html.P("Не удалось построить маршрут между указанными городами.")

    # Создаем полилинию для маршрута
    line = dl.Polyline(positions=route, color='blue')

    # Центрируем карту на первой точке
    center = [city_data_list[0]['lat'], city_data_list[0]['lon']]

    # Создаем объект карты
    map_ = dl.Map(center=center, zoom=5, children=[
        dl.TileLayer(),
        dl.LayerGroup(markers),
        line
    ], style={'width': '100%', 'height': '500px'})

    return map_

if __name__ == "__main__":
    app.run(debug=True)
