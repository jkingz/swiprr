from random import randint

import factory
from crea_parser.models import Parking
from crea_parser.submodels.metadata import PropertyParkingType
from faker import Faker

fake = Faker()


class ParkingFactory(factory.django.DjangoModelFactory):
    """
    Parking Factory
    """

    class Meta:
        model = Parking

    name = factory.Iterator(PropertyParkingType.active_objects.all())
    spaces = factory.LazyAttribute(lambda o: str(randint(0, 100)))

    connected_property = factory.SubFactory(
        "crea_parser.tests.factories.property.PropertyFactory", parking=None
    )
