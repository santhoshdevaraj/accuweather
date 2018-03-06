from collections import defaultdict
from datetime import datetime, timedelta

from django.http import HttpResponseBadRequest
from django_filters import rest_framework as rest_filters
from rest_framework import viewsets, serializers, response, status

from . import models


class LocationSerializer(serializers.ModelSerializer):
    """Serializer for Location model."""

    class Meta:
        fields = '__all__'
        model = models.Location


class WeatherDetailSerializer(serializers.ModelSerializer):
    """Serializer for WeatherDetail model."""

    class Meta:
        fields = ['id', 'date', 'tmax', 'tmin']
        model = models.WeatherDetail

    def to_representation(self, instance, *args, **kwargs):
        """Converts the instance to a serializable format"""
        format = self.context['request'].query_params.get('temp_format', 'fahrenheit')
        if format == 'celsius': instance.tmax, instance.tmin = instance.tmax_in_celsius, instance.tmin_in_celsius
        return super(WeatherDetailSerializer, self).to_representation(instance, *args, **kwargs)


class WeatherDetailFilterSet(rest_filters.FilterSet):
    """Custom filterset for WeatherDetail"""

    FREQUENCY_CHOICES = (('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'))
    FORMAT_CHOICES = (('fahrenheit', 'Temperature in fahrenheit'), ('celsius', 'Temperature in celsius'))

    frequency = rest_filters.ChoiceFilter(
        method='filter_frequency', choices=FREQUENCY_CHOICES, help_text='daily/weekly/monthly. Default is daily'
    )
    start_date = rest_filters.DateFilter(name='date', lookup_expr='gte', help_text='start date (e.g) 2017-06-24')
    end_date = rest_filters.DateFilter(name='date', lookup_expr='lte', help_text='end date (e.g) 2017-06-26')
    city = rest_filters.CharFilter(name='city', lookup_expr='exact', help_text='city name (e.g) BERKHOUT, NL')
    temp_format = rest_filters.ChoiceFilter(
        method='filter_temp_format', choices=FORMAT_CHOICES, help_text='fahrenheit/celsius. Default is fahrenheit'
    )

    class Meta:
        model = models.WeatherDetail
        fields = ['city', 'start_date', 'end_date', 'frequency']

    @staticmethod
    def filter_frequency(queryset, name, value):
        """Returns queryset filtering based on the period selected."""
        return queryset

    @staticmethod
    def filter_temp_format(queryset, name, value):
        """Returns the queryset based on the format as fahrenheit or celsius"""
        return queryset


class WeatherDetailViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return data for a pk

    list:
        Return weather for all days between a range for a city
    """
    filter_class = WeatherDetailFilterSet
    serializer_class = WeatherDetailSerializer
    ordering_fields = '__all__'
    ordering = ('date',)
    http_method_names = ['get', ]

    def get_queryset(self, *args, **kwargs):
        """
        Returns rows from the model without filtering.
        :return: queryset of WeatherDetail objects.
        """
        return models.WeatherDetail.objects.all()

    @staticmethod
    def get_start_of_week_and_month(date_object):
        """
        Given a date object returns start of week and month
        :param date_object: DateTime object
        :return: Returns a tuple of (first day of week e.g '2016-09-29', first day of month e.g '2016-09-01')
        """
        return (
            (date_object - timedelta(days=date_object.weekday())).strftime('%Y-%m-%d'),
            (date_object.replace(day=1)).strftime('%Y-%m-%d')
        )

    @staticmethod
    def get_total_min_and_max_temps(data, frequency):
        """
        Computes the total min and max temperatures for each week or month.
        :param data: data ie a list of maps of temperatures over days between a range
        :param frequency: Frequency requested ie weekly or monthly.
        :return: Map of start_date as key and (total_tmax, total_tmin, days_tmax, days_tmin) as value, where start_date
        is either start of week or month depending on frequency.
        """
        dates_and_temps = defaultdict(lambda: (0, 0, 0, 0))

        for row in data:
            current_date, tmax, tmin = row['date'], row['tmax'], row['tmin']
            start_of_week, start_of_month = \
                WeatherDetailViewSet.get_start_of_week_and_month(datetime.strptime(current_date, '%Y-%m-%d'))
            key = start_of_week if frequency == 'weekly' else start_of_month
            tmax_total, tmin_total, max_days, min_days = dates_and_temps[key]
            dates_and_temps[key] = (
                tmax_total+tmax if tmax else tmax_total,
                tmin_total+tmin if tmin else tmin_total,
                max_days+1 if tmax else max_days,
                min_days+1 if tmin else min_days
            )
        return dates_and_temps

    def get_avg_min_and_max_temps(self, dates_and_temps):
        """
        Computes the average min and max temperatures for each week or month.
        :param dates_and_temps: Map of start_date as key and (total_tmax, total_tmin, days_tmax, days_tmin) as value.
        :return: List of maps of start_date and computed average for that period
        """
        data = []

        for key in dates_and_temps:
            total_tmax, total_tmin, max_days, min_days = dates_and_temps[key]
            data.append({
                "date": key,
                "tmax": round(total_tmax / max_days) if max_days else "N/A",
                "tmin": round(total_tmin / min_days) if min_days else "N/A"
            })

        return data

    def get_updated_response(self, data, frequency):
        """
        Calculates the average of temperatures for each period in the range based on frequency.
        :param data: List of map of temperature data given in daily format over the chosen range.
        :param frequency: Frequency requested e.g 'monthly'.
        :return: List of maps of start_date and computed average for that period.
        """
        dates_and_temps = self.get_total_min_and_max_temps(data, frequency)
        return self.get_avg_min_and_max_temps(dates_and_temps)

    def update_for_frequency(self, response, request):
        """
        Based on the frequency passed updates the API response accordingly.
        :param response: HttpResponse object with temperature data given in daily format over the chosen range.
        :param request: HttpRequest object from the client.
        :return: HttpResponse object with temperature data averaged based on the frequency in incoming request.
        """
        frequency = request.query_params.get('frequency', 'daily')
        return response.data if frequency == 'daily' else self.get_updated_response(response.data, frequency)

    def list(self, request, *args, **kwargs):
        """
        Returns a list of temperature objects for a given city.
        :param request: HttpRequest object.
        :return: HttpResponse with temperature date in daily or weekly or monthly formats.
        :exception: HttpResponseBadRequest if 'city' attribute is not in query params.
        """
        if 'city' not in request.query_params:
            return HttpResponseBadRequest("API can support at most one city's weather data per request")
        api_response = super(WeatherDetailViewSet, self).list(request, *args, **kwargs)
        return response.Response(data=self.update_for_frequency(api_response, request), status=status.HTTP_200_OK)


class LocationViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return data for a pk.

    list:
        Return list of cities with their data.
    """
    serializer_class = LocationSerializer
    ordering_fields = '__all__'
    ordering = ('name', )
    http_method_names = ['get', ]

    def get_queryset(self, *args, **kwargs):
        """
        Returns rows from the model without filtering.
        :return: queryset of Location objects.
        """
        return models.Location.objects.all()
