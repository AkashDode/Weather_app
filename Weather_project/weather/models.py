from django.db import models
from django.utils import timezone


class City(models.Model):
    """Stores tracked cities with their coordinates."""
    name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=5)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timezone = models.CharField(max_length=50, blank=True)
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'cities'
        unique_together = ('name', 'country_code')
        ordering = ['-is_favorite', 'name']

    def __str__(self):
        return f"{self.name}, {self.country_code}"


class WeatherData(models.Model):
    """Stores weather snapshots fetched from the API."""
    CONDITION_CHOICES = [
        ('clear', 'Clear'),
        ('clouds', 'Cloudy'),
        ('rain', 'Rain'),
        ('drizzle', 'Drizzle'),
        ('thunderstorm', 'Thunderstorm'),
        ('snow', 'Snow'),
        ('mist', 'Mist'),
        ('other', 'Other'),
    ]

    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='weather_records')
    fetched_at = models.DateTimeField(default=timezone.now)

    # Temperature
    temperature = models.FloatField(help_text='Temperature in Celsius')
    feels_like = models.FloatField(help_text='Feels like temperature in Celsius')
    temp_min = models.FloatField(help_text='Min temperature in Celsius')
    temp_max = models.FloatField(help_text='Max temperature in Celsius')

    # Conditions
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='other')
    description = models.CharField(max_length=200)
    icon_code = models.CharField(max_length=10)

    # Atmospheric
    humidity = models.IntegerField(help_text='Humidity percentage')
    pressure = models.IntegerField(help_text='Pressure in hPa')
    visibility = models.IntegerField(null=True, blank=True, help_text='Visibility in meters')
    uv_index = models.FloatField(null=True, blank=True)

    # Wind
    wind_speed = models.FloatField(help_text='Wind speed in m/s')
    wind_direction = models.IntegerField(help_text='Wind direction in degrees')
    wind_gust = models.FloatField(null=True, blank=True)

    # Extras
    cloud_coverage = models.IntegerField(help_text='Cloud coverage percentage')
    sunrise = models.DateTimeField(null=True, blank=True)
    sunset = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-fetched_at']
        indexes = [
            models.Index(fields=['city', '-fetched_at']),
        ]

    def __str__(self):
        return f"{self.city} — {self.temperature}°C at {self.fetched_at:%Y-%m-%d %H:%M}"

    @property
    def temperature_f(self):
        return round(self.temperature * 9 / 5 + 32, 1)

    @property
    def wind_speed_kmh(self):
        return round(self.wind_speed * 3.6, 1)

    @property
    def wind_direction_label(self):
        dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        idx = round(self.wind_direction / 45) % 8
        return dirs[idx]


class SearchHistory(models.Model):
    """Tracks user search queries."""
    query = models.CharField(max_length=200)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    searched_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    found_result = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'search histories'
        ordering = ['-searched_at']

    def __str__(self):
        return f'"{self.query}" at {self.searched_at:%Y-%m-%d %H:%M}'


class HourlyForecast(models.Model):
    """Stores hourly forecast data."""
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='hourly_forecasts')
    forecast_time = models.DateTimeField()
    temperature = models.FloatField()
    feels_like = models.FloatField()
    humidity = models.IntegerField()
    wind_speed = models.FloatField()
    description = models.CharField(max_length=200)
    icon_code = models.CharField(max_length=10)
    pop = models.FloatField(default=0, help_text='Probability of precipitation (0-1)')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['forecast_time']
        unique_together = ('city', 'forecast_time')

    def __str__(self):
        return f"{self.city} forecast at {self.forecast_time:%Y-%m-%d %H:%M}"


class DailyForecast(models.Model):
    """Stores daily forecast summaries."""
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='daily_forecasts')
    forecast_date = models.DateField()
    temp_min = models.FloatField()
    temp_max = models.FloatField()
    humidity = models.IntegerField()
    wind_speed = models.FloatField()
    description = models.CharField(max_length=200)
    icon_code = models.CharField(max_length=10)
    pop = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['forecast_date']
        unique_together = ('city', 'forecast_date')

    def __str__(self):
        return f"{self.city} daily forecast for {self.forecast_date}"