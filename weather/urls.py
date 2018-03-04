from django.conf.urls import url, include
from rest_framework.routers import SimpleRouter

from .apis import WeatherDetailViewSet

API_ROUTER = SimpleRouter(trailing_slash=True)
API_ROUTER.register('weather_detail', WeatherDetailViewSet, base_name='weather_detail')

urlpatterns = [
    url('', include(API_ROUTER.urls)),
]