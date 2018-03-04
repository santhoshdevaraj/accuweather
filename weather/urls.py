from django.conf.urls import url, include
from rest_framework.routers import SimpleRouter

from .apis import WeatherDetailViewSet, LocationViewSet

API_ROUTER = SimpleRouter(trailing_slash=True)
API_ROUTER.register('weather', WeatherDetailViewSet, base_name='weather_detail')
API_ROUTER.register('cities', LocationViewSet, base_name='city_detail')

urlpatterns = [
    url('', include(API_ROUTER.urls)),
]