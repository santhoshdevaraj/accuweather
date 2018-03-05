"""Unit test for API end points."""

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
        self.assertEqual(len(response_list), len(city_weather))
        self.assertEqual([i['city'] for i in response_list].count('city_0'), len(city_weather))

    def test_filter_between_date_range(self):
        """GET with start date and end date filter applied should fetch everything in range"""
        city_weather = models.WeatherDetail.objects.filter(city='city_1').order_by('date')
        start_date, end_date = city_weather[2].date, city_weather[5].date
        input_dates = [o.date.strftime('%Y-%m-%d') for o in city_weather[2:6]]
        response = self.api_client.get('/api/weather/?city=city_1&start_date={}&end_date={}'.format(start_date, end_date))
        response_list = response.json()
        self.assertEqual(len(response_list), 4)
        output_dates = sorted([o['date'] for o in response_list])
        self.assertEqual(input_dates, output_dates)

    def test_filter_by_frequency_daily(self):
        """GET with frequency filter applied on daily basis should fetch data in range"""
        pass

    def test_filter_by_frequency_weekly(self):
        """GET with frequency filter applied on weekly basis should fetch data in range"""
        pass

    def test_filter_by_frequency_monthly(self):
        """GET with frequency filter applied on monthly basis should fetch data in range"""
        pass

    def test_filter_by_format(self):
        """GET with filter by temperature format as celsius or fahrenheit should return data"""
        pass

    def test_get_city_weather_by_pk(self):
        """GET with a pk should return 1 row."""
        weather = models.WeatherDetail.objects.first()
        response = self.api_client.get('/api/weather/{}/'.format(weather.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json()
        self.assertEqual(response_dict['id'], weather.id)
        self.assertIn('date', response_dict)
        self.assertIn('city', response_dict)
        self.assertIn('tmax', response_dict)
        self.assertIn('tmin', response_dict)

    def test_get_cities_list(self):
        """GET on location end point should return the list of cities"""
        pass
