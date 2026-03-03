"""
Weather service — handles all OpenWeatherMap API interactions and DB persistence.
"""

import requests
from datetime import datetime, timezone as dt_tz
from django.conf import settings
from django.utils import timezone

from .models import City, WeatherData, HourlyForecast, DailyForecast, SearchHistory


class WeatherAPIError(Exception):
    pass


def _get(endpoint, params):
    """Make a GET request to the OpenWeatherMap API."""
    params['appid'] = settings.OPENWEATHER_API_KEY
    params['units'] = 'metric'
    url = settings.OPENWEATHER_BASE_URL + endpoint
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        raise WeatherAPIError("Could not connect to the weather service. Check your internet connection.")
    except requests.exceptions.Timeout:
        raise WeatherAPIError("Weather service timed out. Please try again.")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise WeatherAPIError("Invalid API key. Please configure OPENWEATHER_API_KEY.")
        elif e.response.status_code == 404:
            raise WeatherAPIError("City not found.")
        raise WeatherAPIError(f"Weather API error: {e}")


def _condition_key(main):
    mapping = {
        'Clear': 'clear', 'Clouds': 'clouds', 'Rain': 'rain',
        'Drizzle': 'drizzle', 'Thunderstorm': 'thunderstorm',
        'Snow': 'snow', 'Mist': 'mist', 'Fog': 'mist', 'Haze': 'mist',
    }
    return mapping.get(main, 'other')


def _from_unix(ts):
    if ts is None:
        return None
    return datetime.fromtimestamp(ts, tz=dt_tz.utc)


def get_current_weather(city_name, ip_address=None):
    """
    Fetch current weather for city_name, persist to DB, return WeatherData instance.
    Also records the search in SearchHistory.
    """
    data = _get('weather', {'q': city_name})

    # Upsert City
    city, _ = City.objects.update_or_create(
        name=data['name'],
        country_code=data['sys']['country'],
        defaults={
            'latitude': data['coord']['lat'],
            'longitude': data['coord']['lon'],
        }
    )

    # Build WeatherData record
    wd = WeatherData.objects.create(
        city=city,
        temperature=data['main']['temp'],
        feels_like=data['main']['feels_like'],
        temp_min=data['main']['temp_min'],
        temp_max=data['main']['temp_max'],
        condition=_condition_key(data['weather'][0]['main']),
        description=data['weather'][0]['description'].title(),
        icon_code=data['weather'][0]['icon'],
        humidity=data['main']['humidity'],
        pressure=data['main']['pressure'],
        visibility=data.get('visibility'),
        wind_speed=data['wind']['speed'],
        wind_direction=data['wind'].get('deg', 0),
        wind_gust=data['wind'].get('gust'),
        cloud_coverage=data['clouds']['all'],
        sunrise=_from_unix(data['sys'].get('sunrise')),
        sunset=_from_unix(data['sys'].get('sunset')),
    )

    # Record search
    SearchHistory.objects.create(
        query=city_name,
        city=city,
        ip_address=ip_address,
        found_result=True,
    )

    return wd


def get_forecast(city):
    """Fetch 5-day / 3-hour forecast and persist hourly + daily records."""
    data = _get('forecast', {'lat': city.latitude, 'lon': city.longitude})

    # Clear old forecasts for this city
    HourlyForecast.objects.filter(city=city).delete()
    DailyForecast.objects.filter(city=city).delete()

    daily_buckets = {}

    for item in data['list']:
        ft = _from_unix(item['dt'])
        HourlyForecast.objects.create(
            city=city,
            forecast_time=ft,
            temperature=item['main']['temp'],
            feels_like=item['main']['feels_like'],
            humidity=item['main']['humidity'],
            wind_speed=item['wind']['speed'],
            description=item['weather'][0]['description'].title(),
            icon_code=item['weather'][0]['icon'],
            pop=item.get('pop', 0),
        )
        date_key = ft.date()
        if date_key not in daily_buckets:
            daily_buckets[date_key] = {
                'temps': [], 'humidity': [], 'wind': [],
                'description': item['weather'][0]['description'].title(),
                'icon_code': item['weather'][0]['icon'],
                'pop': item.get('pop', 0),
            }
        b = daily_buckets[date_key]
        b['temps'].append(item['main']['temp'])
        b['humidity'].append(item['main']['humidity'])
        b['wind'].append(item['wind']['speed'])
        b['pop'] = max(b['pop'], item.get('pop', 0))

    for date_key, b in daily_buckets.items():
        DailyForecast.objects.create(
            city=city,
            forecast_date=date_key,
            temp_min=min(b['temps']),
            temp_max=max(b['temps']),
            humidity=round(sum(b['humidity']) / len(b['humidity'])),
            wind_speed=round(sum(b['wind']) / len(b['wind']), 1),
            description=b['description'],
            icon_code=b['icon_code'],
            pop=b['pop'],
        )

    return {
        'hourly': list(HourlyForecast.objects.filter(city=city)[:24]),
        'daily': list(DailyForecast.objects.filter(city=city)),
    }


def get_favorite_cities_weather():
    """Fetch latest stored weather for all favorite cities."""
    favorites = City.objects.filter(is_favorite=True)
    results = []
    for city in favorites:
        latest = city.weather_records.first()
        if latest:
            results.append(latest)
    return results


def record_failed_search(query, ip_address=None):
    SearchHistory.objects.create(
        query=query,
        ip_address=ip_address,
        found_result=False,
    )