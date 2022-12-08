from random import randint

import factory
from core.tests.utils import produce_fake_random_words_or_none
from crea_parser.models import Building
from faker import Faker

fake = Faker()


class BuildingFactory(factory.django.DjangoModelFactory):
    """
    Building Factory
    """

    class Meta:
        model = Building

    bathroom_total = factory.LazyAttribute(lambda o: randint(1, 100))
    bedrooms_total = factory.LazyAttribute(lambda o: randint(1, 100))

    connected_property = factory.SubFactory(
        "crea_parser.tests.factories.property.PropertyFactory", building=None
    )
