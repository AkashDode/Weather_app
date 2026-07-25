from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('city/<int:city_id>/', views.city_detail, name='city_detail'),
    path('city/<int:city_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('city/<int:city_id>/refresh/', views.refresh_weather, name='refresh_weather'),
    path('cities/', views.cities_list, name='cities_list'),
    path('history/', views.search_history_view, name='search_history'),
    path('api/weather/<int:city_id>/', views.api_weather, name='api_weather'),
]