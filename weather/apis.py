from rest_framework import viewsets, response, serializers, status

from . import models


class WeatherDetailSerializer(serializers.ModelSerializer):
    """Serializer for WeatherDetail model."""

    class Meta:
        fields = '__all__'
        model = models.WeatherDetail


class WeatherDetailViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return data for a single day

    list:
        Return weather for all days between a range
    """
    serializer_class = WeatherDetailSerializer
    ordering_fields = '__all__'
    http_method_names = ['get', ]

    def get_queryset(self, *args, **kwargs):
        return models.WeatherDetail.objects.all()