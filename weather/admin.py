from django.contrib import admin
from .models import City, WeatherData, SearchHistory, HourlyForecast, DailyForecast


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country_code', 'latitude', 'longitude', 'is_favorite', 'created_at')
    list_filter = ('country_code', 'is_favorite')
    search_fields = ('name', 'country_code')
    list_editable = ('is_favorite',)


@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ('city', 'temperature', 'condition', 'humidity', 'wind_speed', 'fetched_at')
    list_filter = ('condition', 'city')
    search_fields = ('city__name',)
    date_hierarchy = 'fetched_at'
    readonly_fields = ('fetched_at',)


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('query', 'city', 'found_result', 'ip_address', 'searched_at')
    list_filter = ('found_result',)
    search_fields = ('query', 'city__name')
    date_hierarchy = 'searched_at'
    readonly_fields = ('searched_at',)


@admin.register(HourlyForecast)
class HourlyForecastAdmin(admin.ModelAdmin):
    list_display = ('city', 'forecast_time', 'temperature', 'description', 'pop')
    list_filter = ('city',)
    date_hierarchy = 'forecast_time'


@admin.register(DailyForecast)
class DailyForecastAdmin(admin.ModelAdmin):
    list_display = ('city', 'forecast_date', 'temp_min', 'temp_max', 'description', 'pop')
    list_filter = ('city',)
    date_hierarchy = 'forecast_date'