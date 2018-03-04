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


class WeatherDetailViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return data for a pk

    list:
        Return weather for all days between a range
    """
    filter_fields = ('station', 'name')
    serializer_class = WeatherDetailSerializer
    ordering_fields = '__all__'
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
    http_method_names = ['get', ]

    def get_queryset(self, *args, **kwargs):
        return models.Location.objects.all()
