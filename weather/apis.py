from django_filters import rest_framework as rest_filters
from rest_framework import viewsets, serializers

from . import models


class WeatherDetailSerializer(serializers.ModelSerializer):
    """Serializer for WeatherDetail model."""

    class Meta:
        fields = '__all__'
        model = models.WeatherDetail


class LocationSerializer(serializers.ModelSerializer):
    """Serializer for WeatherDetail model."""

    class Meta:
        fields = '__all__'
        model = models.Location

    def to_representation(self, obj):
        location_obj = super(LocationSerializer, self).to_representation(obj)
        return location_obj['name']


class WeatherDetailFilterSet(rest_filters.FilterSet):
    """Custom filterset for WeatherDetail"""
    start_date = rest_filters.DateFilter(name='date', lookup_expr='gte')
    end_date = rest_filters.DateFilter(name='date', lookup_expr='lte')

    class Meta:
        model = models.WeatherDetail
        fields = ['station', 'city', 'start_date', 'end_date']


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


class LocationViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return data for a pk

    list:
        Return all stations and cities. Use 'type' filter to view 'station' or 'city' list.
    """
    filter_fields = ('type', )
    serializer_class = LocationSerializer
    ordering_fields = '__all__'
    ordering = ('name', )
    http_method_names = ['get', ]

    def get_queryset(self, *args, **kwargs):
        return models.Location.objects.all()
