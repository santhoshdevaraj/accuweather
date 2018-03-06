"""Unit test for API end points."""

from datetime import timedelta
from collections import defaultdict

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from weather import models
from . import factories


class APITestCase(TestCase):
    """Test helpers for API viewsets."""
    @classmethod
    def setUpClass(cls):
        TestCase.setUpClass()
        cls.api_client = APIClient()
        factories.LocationFactory.reset_sequence(force=True)
        factories.WeatherDetailFactory.reset_sequence(force=True)
        cities = factories.LocationFactory.create_batch(3)
        for city in cities:
            factories.WeatherDetailFactory.create_batch(20, city=city)

    @classmethod
    def tearDownClass(cls):
        TestCase.tearDownClass()
        models.WeatherDetail.objects.all().delete()
        models.Location.objects.all().delete()

    def test_city_is_mandatory(self):
        """GET without a city param should return a bad request (400) response"""
        response = self.api_client.get('/api/weather/?frequency=monthly')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_city_data_is_fetched(self):
        """GET with 'city' param should return data in the DB"""
        city_weather = models.WeatherDetail.objects.filter(city='city_0')
        response = self.api_client.get('/api/weather/?city=city_0')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_list = response.json()
        self.assertIsInstance(response_list, list)
        self.assertEqual(len(response_list), len(city_weather))
        city_data = response_list[0]
        self.assertIn("id", city_data)
        self.assertIn("date", city_data)
        self.assertIn("tmax", city_data)
        self.assertIn("tmin", city_data)

    def test_filter_by_daily_between_date_range(self):
        """GET with start date and end date filter applied should fetch everything in range"""
        city_weather = models.WeatherDetail.objects.filter(city='city_1').order_by('date')
        start_date, end_date = city_weather[2].date, city_weather[5].date
        input_dates = sorted(list(set([o.date.strftime('%Y-%m-%d') for o in city_weather[2:6]])))
        response = self.api_client.get('/api/weather/?city=city_1&start_date={}&end_date={}'.format(start_date, end_date))
        response_list = response.json()
        output_dates = sorted(set([o['date'] for o in response_list]))
        self.assertEqual(input_dates, output_dates)

    def test_filter_by_frequency_weekly(self):
        """GET with frequency filter applied on weekly basis should fetch data in range"""
        city_weather = models.WeatherDetail.objects.filter(city='city_2').order_by('date')
        week_map = defaultdict(lambda: (0, 0, 0, 0))

        for row in city_weather:
            date_object = row.date
            start_of_week = (date_object - timedelta(days=date_object.weekday())).strftime('%Y-%m-%d')
            max_temp, min_temp = row.tmax, row.tmin
            total_max, days_max, total_min, days_min = week_map[start_of_week]
            week_map[start_of_week] = (
                total_max + (max_temp or 0),
                days_max + (1 if max_temp else 0),
                total_min + (min_temp or 0),
                days_min + (1 if min_temp else 0)
            )
        response = self.api_client.get('/api/weather/?city=city_2&frequency=weekly')
        response_list = response.json()
        weekly_data = response_list[0]
        self.assertIn("date", weekly_data)
        self.assertIn("tmax", weekly_data)
        self.assertIn("tmin", weekly_data)

        for row in response_list:
            week = row['date']
            total_max, days_max, total_min, days_min = week_map[week]
            self.assertEqual(row['tmax'], round(total_max/days_max))
            self.assertEqual(row['tmin'], round(total_min/days_min))

    def test_filter_by_frequency_monthly(self):
        """GET with frequency filter applied on monthly basis should fetch data in range"""
        city_weather = models.WeatherDetail.objects.filter(city='city_0').order_by('date')
        month_map = defaultdict(lambda: (0, 0, 0, 0))

        for row in city_weather:
            date_object = row.date
            start_of_month = (date_object.replace(day=1)).strftime('%Y-%m-%d')
            max_temp, min_temp = row.tmax, row.tmin
            total_max, days_max, total_min, days_min = month_map[start_of_month]
            month_map[start_of_month] = (
                total_max + (max_temp or 0),
                days_max + (1 if max_temp else 0),
                total_min + (min_temp or 0),
                days_min + (1 if min_temp else 0)
            )
        response = self.api_client.get('/api/weather/?city=city_0&frequency=monthly')
        response_list = response.json()
        weekly_data = response_list[0]
        self.assertIn("date", weekly_data)
        self.assertIn("tmax", weekly_data)
        self.assertIn("tmin", weekly_data)

        for row in response_list:
            month = row['date']
            total_max, days_max, total_min, days_min = month_map[month]
            self.assertEqual(row['tmax'], round(total_max / days_max))
            self.assertEqual(row['tmin'], round(total_min / days_min))

    def test_filter_by_format(self):
        """GET with filter by temperature format as celsius or fahrenheit should return data"""
        city_weather = models.WeatherDetail.objects.filter(city='city_0').first()
        city_weather_id = city_weather.id
        response = self.api_client.get('/api/weather/%s/?temp_format=celsius' %(city_weather_id))
        response_data = response.json()
        tmax_in_celsius = round((city_weather.tmax - 32) * (5/9))
        tmin_in_celsius = round((city_weather.tmin - 32) * (5 / 9))
        self.assertEqual(tmax_in_celsius, response_data['tmax'])
        self.assertEqual(tmin_in_celsius, response_data['tmin'])
        response = self.api_client.get('/api/weather/%s/?temp_format=fahrenheit' % (city_weather_id))
        response_data = response.json()
        self.assertEqual(city_weather.tmax, response_data['tmax'])
        self.assertEqual(city_weather.tmin, response_data['tmin'])

    def test_get_city_weather_by_pk(self):
        """GET with a pk should return 1 row."""
        weather = models.WeatherDetail.objects.first()
        response = self.api_client.get('/api/weather/{}/'.format(weather.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json()
        self.assertEqual(response_dict['id'], weather.id)
        self.assertIn('date', response_dict)
        self.assertIn('tmax', response_dict)
        self.assertIn('tmin', response_dict)

    def test_get_cities_list(self):
        """GET on location end point should return the list of cities"""
        cities = models.Location.objects.all().count()
        response = self.api_client.get('/api/cities/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_list = response.json()
        self.assertEqual(len(response_list), cities)
        self.assertIn("name", response_list[0])
        self.assertIn("latitude", response_list[0])
        self.assertIn("longitude", response_list[0])
        self.assertIn("elevation", response_list[0])
