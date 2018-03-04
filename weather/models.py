
from django.db import models


class WeatherDetail(models.Model):
    """Object for storing the daily weather data."""
    city = models.ForeignKey('Location', related_name='city_name')
    date = models.DateField()
    tmax = models.IntegerField(null=True)
    tmin = models.IntegerField(null=True)

    @staticmethod
    def convert_fahrenheit_to_celsius(value):
        """converts fahrenheit to celsius"""
        return round((value - 32) * (5/9))

    @property
    def tmin_in_celsius(self):
        return self.convert_fahrenheit_to_celsius(self.tmin)

    @property
    def tmax_in_celsius(self):
        return self.convert_fahrenheit_to_celsius(self.tmax)


class Location(models.Model):
    """Object representing the various cities"""
    name = models.TextField(primary_key=True)
    station = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=10, decimal_places=6)
    longitude = models.DecimalField(max_digits=10, decimal_places=6)
    elevation = models.DecimalField(max_digits=10, decimal_places=4)
