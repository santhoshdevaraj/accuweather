import datetime
import random
import factory.fuzzy


class LocationFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'weather.Location'

    name = factory.Sequence('city_{}'.format)
    station = factory.Sequence('station_{}'.format)
    latitude = factory.Sequence(lambda n: n)
    longitude = factory.Sequence(lambda n: n)
    elevation = factory.Sequence(lambda n: n)


class WeatherDetailFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'weather.WeatherDetail'

    city = factory.SubFactory(LocationFactory)
    date = factory.fuzzy.FuzzyDate(start_date=datetime.date(2016, 9, 1), end_date=datetime.date(2017, 9, 1))
    tmax = factory.Sequence(lambda n: random.randint(20, 50))
    tmin = factory.LazyAttribute(lambda o: o.tmax - random.randint(1, 20))
