from django.http import HttpResponseBadRequest

from django_filters import rest_framework as rest_filters
from rest_framework import viewsets, serializers

from . import models


class LocationSerializer(serializers.ModelSerializer):
    """Serializer for WeatherDetail model."""

    class Meta:
        fields = '__all__'
        model = models.Location


class WeatherDetailSerializer(serializers.ModelSerializer):
    """Serializer for WeatherDetail model."""

    class Meta:
        fields = ['id', 'date', 'tmax', 'tmin']
        model = models.WeatherDetail


class WeatherDetailFilterSet(rest_filters.FilterSet):
    """Custom filterset for WeatherDetail"""
    start_date = rest_filters.DateFilter(name='date', lookup_expr='gte')
    end_date = rest_filters.DateFilter(name='date', lookup_expr='lte')

    class Meta:
        model = models.WeatherDetail
        fields = ['city', 'start_date', 'end_date']


class WeatherDetailViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return data for a pk

    list:
        Return weather for all days between a range
    """
    filter_class = WeatherDetailFilterSet
    serializer_class = WeatherDetailSerializer
    ordering_fields = '__all__'
    ordering = ('date',)
    http_method_names = ['get', ]

    def get_queryset(self, *args, **kwargs):
        return models.WeatherDetail.objects.all()

    def list(self, request, *args, **kwargs):
        if 'city' not in request.query_params:
            return HttpResponseBadRequest("API can support at most one city's weather data per request")
        return super(WeatherDetailViewSet, self).list(request, *args, **kwargs)


class LocationViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return data for a pk

    list:
        Return list of cities with their data
    """
    serializer_class = LocationSerializer
    ordering_fields = '__all__'
    ordering = ('name', )
    http_method_names = ['get', ]

    def get_queryset(self, *args, **kwargs):
        return models.Location.objects.all()
