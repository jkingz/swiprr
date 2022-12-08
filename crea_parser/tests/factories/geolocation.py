import factory
from crea_parser.models import Geolocation
from django.contrib.gis.geos import Point
from faker import Faker

fake = Faker()


class GeoLocationFactory(factory.django.DjangoModelFactory):
    """
    Geolocation Factory
    """

    class Meta:
        model = Geolocation

    coordinates = factory.LazyAttribute(
        lambda o: Point(float(fake.longitude()), float(fake.latitude()))
    )

    connected_property = factory.SubFactory(
        "crea_parser.tests.factories.property.PropertyFactory", geo_location=None
    )
