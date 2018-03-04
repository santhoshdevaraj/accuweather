from collections import defaultdict
from datetime import datetime

from django.http import HttpResponseBadRequest

from django_filters import rest_framework as rest_filters
from rest_framework import viewsets, serializers, response, status

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
    frequency = rest_filters.CharFilter(method='filter_frequency')
    start_date = rest_filters.DateFilter(name='date', lookup_expr='gte')
    end_date = rest_filters.DateFilter(name='date', lookup_expr='lte')

    class Meta:
        model = models.WeatherDetail
        fields = ['city', 'start_date', 'end_date']

    @staticmethod
    def filter_frequency(queryset, name, value):
        """Returns queryset filtering based on the period selected."""
        return queryset


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

    def create_weekly_response(self, response):
        pass

    def create_monthly_response(self, response):
        """Updates the response with the year and month and average for that month"""
        data_map = defaultdict(lambda : (0, 0, 0, 0))
        data = response.data

        for row in data:
            current_date, tmax, tmin = row['date'], row['tmax'], row['tmin']
            date_object = datetime.strptime(current_date, '%Y-%m-%d')
            year, month = date_object.year, date_object.strftime('%B')
            tmax_total, tmin_total, max_days, min_days = data_map[(year, month)]
            data_map[(year, month)] = (
                tmax_total+tmax if tmax else tmax_total,
                tmin_total+tmin if tmin else tmin_total,
                max_days+1 if tmax else max_days,
                min_days+1 if tmin else min_days
            )

        monthly_data = []

        for key in data_map:
            total_tmax, total_tmin, max_days, min_days, year, month = *data_map[key], *key
            monthly_data.append({
                "year": year,
                "month": month,
                "avg_max": round(total_tmax/max_days) if max_days else "N/A",
                "avg_min": round(total_tmin/min_days) if min_days else "N/A"
            })

        return monthly_data

    def update_for_frequency(self, response, request):
        """Based on the frequency passed updates the API response accordingly"""
        frequency = request.query_params.get('frequency', None)
        if frequency == 'weekly':
            return self.create_weekly_response(response)
        elif frequency == 'monthly':
            return self.create_monthly_response(response)
        return response.data

    def list(self, request, *args, **kwargs):
        if 'city' not in request.query_params:
            return HttpResponseBadRequest("API can support at most one city's weather data per request")
        api_response = super(WeatherDetailViewSet, self).list(request, *args, **kwargs)
        return response.Response(data=self.update_for_frequency(api_response, request), status=status.HTTP_200_OK)


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
