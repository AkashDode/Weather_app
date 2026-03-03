from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import City, WeatherData, SearchHistory
from .services import (
    get_current_weather, get_forecast,
    WeatherAPIError, record_failed_search,
    get_favorite_cities_weather,
)


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def home(request):
    """Home page — search form + favorites."""
    favorites_weather = get_favorite_cities_weather()
    recent_searches = SearchHistory.objects.filter(found_result=True).select_related('city')[:8]
    context = {
        'favorites_weather': favorites_weather,
        'recent_searches': recent_searches,
        'page': 'home',
    }
    return render(request, 'weather/home.html', context)


def search(request):
    """Handle city search and redirect to detail page."""
    city_name = request.GET.get('q', '').strip()
    if not city_name:
        messages.warning(request, 'Please enter a city name.')
        return redirect('weather:home')

    ip = get_client_ip(request)
    try:
        weather_data = get_current_weather(city_name, ip_address=ip)
        return redirect('weather:city_detail', city_id=weather_data.city.id)
    except WeatherAPIError as e:
        record_failed_search(city_name, ip_address=ip)
        messages.error(request, str(e))
        return redirect('weather:home')


def city_detail(request, city_id):
    """Detailed weather page for a specific city."""
    city = get_object_or_404(City, id=city_id)
    latest_weather = city.weather_records.first()

    # Fetch fresh data if no record or older than 30 minutes
    refresh = False
    if not latest_weather:
        refresh = True
    else:
        age = (timezone.now() - latest_weather.fetched_at).total_seconds()
        if age > 1800:
            refresh = True

    if refresh:
        try:
            latest_weather = get_current_weather(f"{city.name},{city.country_code}")
        except WeatherAPIError as e:
            messages.error(request, str(e))

    # Get forecasts
    forecasts = {}
    if city.daily_forecasts.exists():
        forecasts['daily'] = list(city.daily_forecasts.all()[:7])
        forecasts['hourly'] = list(city.hourly_forecasts.all()[:24])
    else:
        try:
            forecasts = get_forecast(city)
        except WeatherAPIError:
            pass

    # Historical data for chart (last 24 records)
    history = list(city.weather_records.all()[:24])
    history.reverse()
    chart_labels = [w.fetched_at.strftime('%H:%M') for w in history]
    chart_temps = [round(w.temperature, 1) for w in history]

    context = {
        'city': city,
        'weather': latest_weather,
        'forecasts': forecasts,
        'chart_labels': chart_labels,
        'chart_temps': chart_temps,
        'page': 'detail',
    }
    return render(request, 'weather/city_detail.html', context)


@require_POST
def toggle_favorite(request, city_id):
    """Toggle a city's favorite status."""
    city = get_object_or_404(City, id=city_id)
    city.is_favorite = not city.is_favorite
    city.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'is_favorite': city.is_favorite})
    return redirect('weather:city_detail', city_id=city.id)


def cities_list(request):
    """List all tracked cities."""
    cities = City.objects.prefetch_related('weather_records').all()
    cities_data = []
    for city in cities:
        latest = city.weather_records.first()
        cities_data.append({'city': city, 'weather': latest})

    context = {
        'cities_data': cities_data,
        'page': 'cities',
    }
    return render(request, 'weather/cities_list.html', context)


def search_history_view(request):
    """View search history log."""
    history = SearchHistory.objects.select_related('city').all()[:100]
    context = {
        'history': history,
        'page': 'history',
    }
    return render(request, 'weather/search_history.html', context)


def api_weather(request, city_id):
    """JSON API endpoint for weather data."""
    city = get_object_or_404(City, id=city_id)
    weather = city.weather_records.first()
    if not weather:
        return JsonResponse({'error': 'No data available'}, status=404)

    return JsonResponse({
        'city': str(city),
        'temperature': weather.temperature,
        'feels_like': weather.feels_like,
        'condition': weather.condition,
        'description': weather.description,
        'humidity': weather.humidity,
        'wind_speed': weather.wind_speed,
        'wind_direction': weather.wind_direction_label,
        'pressure': weather.pressure,
        'cloud_coverage': weather.cloud_coverage,
        'fetched_at': weather.fetched_at.isoformat(),
    })


def refresh_weather(request, city_id):
    """Force-refresh weather data for a city."""
    city = get_object_or_404(City, id=city_id)
    try:
        get_current_weather(f"{city.name},{city.country_code}")
        get_forecast(city)
        messages.success(request, f'Weather for {city.name} refreshed successfully.')
    except WeatherAPIError as e:
        messages.error(request, str(e))
    return redirect('weather:city_detail', city_id=city.id)