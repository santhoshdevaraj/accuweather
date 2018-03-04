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
        fields = ['id', 'city', 'date', 'tmax', 'tmin']
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
    def get_year_month_week(date_object):
        """
        Given a date object returns the year, month and start of week
        :param date_object: DateTime object
        :return: Returns a tuple of (year e.g 2016, month e.g 'September', first day of week e.g '2016-09-29')
        """
        return (
            date_object.year,
            date_object.strftime('%B'),
            (date_object - timedelta(days=date_object.weekday())).strftime('%Y-%m-%d')
        )

    @staticmethod
    def create_data_map(data, data_map, frequency):
        """
        :param data: HttpResponse.data ie a list of maps of temperatures over days between a range
        :param data_map: Defaultdict with (0, 0, 0, 0) as default value.
        :param frequency: Frequency requested ie weekly or monthly.
        :return: Map of (year, period) as key and (total_tmax, total_tmin, days_tmax, days_tmin) as value where period
                is either monthly or weekly depending on frequency
        """
        for row in data:
            current_date, tmax, tmin = row['date'], row['tmax'], row['tmin']
            year, month, week = WeatherDetailViewSet.get_year_month_week(datetime.strptime(current_date, '%Y-%m-%d'))
            key = (year, month) if frequency == 'month' else (year, week)

            tmax_total, tmin_total, max_days, min_days = data_map[key]
            data_map[key] = (
                tmax_total+tmax if tmax else tmax_total,
                tmin_total+tmin if tmin else tmin_total,
                max_days+1 if tmax else max_days,
                min_days+1 if tmin else min_days
            )
        return data_map

    def get_response(self, data_map, frequency):
        """
        Creates the response, based on the frequency selected.
        :param data_map: Map of (year, frequency) as key and (total_tmax, total_tmin, days_tmax, days_tmin) as value.
        :param frequency: Frequency requested ie weekly or monthly.
        :return: Computes the average of tmax and tmin for each period and returns a map of {year, period, avg_max,
                avg_min}. (e.g) when frequency is 'monthly', {year: 2016, month: 'September', avg_max: 20,
                avg_min: 30}. When frequency is 'weekly', {year: 2016, week: '2016-09-29', avg_max: 20, avg_min: 30}
        """
        data = []

        for key in data_map:
            total_tmax, total_tmin, max_days, min_days, year, freq_value = *data_map[key], *key
            data.append({
                'year': year,
                frequency: freq_value,
                "avg_max": round(total_tmax / max_days) if max_days else "N/A",
                "avg_min": round(total_tmin / min_days) if min_days else "N/A"
            })

        return data

    def create_weekly_response(self, response, frequency):
        """
        Updates the response with the year, week and average for that week.
        :param response: HttpResponse object with temperature data given in daily format over the chosen range.
        :param frequency: Frequency requested ie 'weekly'.
        :return: A list of map of {year, period, avg_max, avg_min} for each period in the date range, where period
                is the first day of each week for the date range.
        """
        data_map = self.create_data_map(response.data, defaultdict(lambda: (0, 0, 0, 0)), frequency)
        return self.get_response(data_map, frequency)

    def create_monthly_response(self, response, frequency):
        """
        Updates the response with the year, month and average for that month.
        :param response: HttpResponse object with temperature data given in daily format over the chosen range.
        :param frequency: Frequency requested ie 'monthly'.
        :return: A list of map of {year, period, avg_max, avg_min} for each period in the date range, where period
                is each month for the date range.
        """
        data_map = self.get_data_map(response.data, defaultdict(lambda : (0, 0, 0, 0)), frequency)
        return self.get_response(data_map, frequency)

    def update_for_frequency(self, response, request):
        """
        Based on the frequency passed updates the API response accordingly.
        :param response: HttpResponse object with temperature data given in daily format over the chosen range.
        :param request: HttpRequest object from the client.
        :return: HttpResponse object with temperature data averaged based on the frequency in incoming request.
        """
        frequency = request.query_params.get('frequency', None)
        if frequency == 'weekly':
            return self.create_weekly_response(response, 'week')
        elif frequency == 'monthly':
            return self.create_monthly_response(response, 'month')
        return response.data

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
