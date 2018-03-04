# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-04 01:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('location', models.TextField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='LocationType',
            fields=[
                ('type', models.CharField(choices=[('station', 'Weather Station'), ('city', 'City')], max_length=30, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='WeatherDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=10)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=10)),
                ('elevation', models.DecimalField(decimal_places=4, max_digits=10)),
                ('date', models.DateField()),
                ('tmax', models.IntegerField(null=True)),
                ('tmin', models.IntegerField(null=True)),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='city_name', to='weather.Location')),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='weather_station', to='weather.Location')),
            ],
        ),
        migrations.AddField(
            model_name='location',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='weather.LocationType'),
        ),
    ]