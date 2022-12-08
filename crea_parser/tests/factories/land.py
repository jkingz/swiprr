from random import randint

import factory
from crea_parser.models import Land
from faker import Faker

fake = Faker()


class LandFactory(factory.django.DjangoModelFactory):
    """
    Land Factory
    """

    class Meta:
        model = Land

    connected_property = factory.SubFactory(
        "crea_parser.tests.factories.property.PropertyFactory", land=None
    )
