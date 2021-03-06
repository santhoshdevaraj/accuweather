import csv

from django.core.management import BaseCommand

from weather import models


class Command(BaseCommand):
    """Management command for loading the csv file to DB"""

    help = 'Loads the weather data from CSV file to relevant model'

    def add_arguments(self, parser):
        """Adds the required options to be passed to the file load"""
        parser.add_argument(
            '--file', dest='file', required=True,
            help='the path for the file to upload',
        )

    def cleanup_model(self):
        """Removes existing rows in the model before data load"""
        return models.WeatherDetail.objects.all().delete() and \
            models.Location.objects.all().delete()

    @staticmethod
    def create_locations(data):
        """Create the location object ie station or city"""
        cities = {(row[0], row[1], row[2], row[3], row[4]) for row in data}
        locations = (
            [models.Location(name=city, station=station, latitude=latitude, longitude=longitude, elevation=elevation)
                for city_data in cities for (station, city, latitude, longitude, elevation) in (city_data,)]
        )
        return models.Location.objects.bulk_create(locations)

    @staticmethod
    def create_weather_detail(data):
        """Create the weather detail object in the DB"""
        weather_detail = [models.WeatherDetail(city_id=row[1], date=row[5], tmax=row[6] or None, tmin=row[7] or None)
            for row in data]
        return models.WeatherDetail.objects.bulk_create(weather_detail)

    def handle(self, *args, **options):
        """Entry point for running the management command"""
        print("Starting csv file upload")
        file_path = options['file']

        with open(file_path, 'r') as csvfile:
            print("Opened the file `{}` for upload in read mode".format(file_path))
            self.cleanup_model()
            print("Removed existing data from DB")
            csv_data = [row for row in csv.reader(csvfile, delimiter='\t')][1:]
            self.create_locations(csv_data)
            self.create_weather_detail(csv_data)

        print("Completed csv file upload successfully")
