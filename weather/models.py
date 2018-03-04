
from django.db import models


class WeatherDetail(models.Model):
    """Object for storing the daily weather data."""
    station = models.ForeignKey('Location', related_name='station_name')
    city = models.ForeignKey('Location', related_name='city_name')
    date = models.DateField()
    tmax = models.IntegerField(null=True)
    tmin = models.IntegerField(null=True)


class Location(models.Model):
    """Object representing the various locations"""
    name = models.TextField(primary_key=True)
    type = models.ForeignKey('LocationType')
    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    elevation = models.DecimalField(max_digits=10, decimal_places=4, null=True)


class LocationType(models.Model):
    """Object representing the location category"""
    TYPES = (('station', 'Weather Station'), ('city', 'City'))
    type = models.CharField(primary_key=True, max_length=30, choices=TYPES)
