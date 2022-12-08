import factory
from crea_parser.models import Utility
from crea_parser.submodels.metadata import PropertyUtilityType
from faker import Faker

fake = Faker()


class UtilityFactory(factory.django.DjangoModelFactory):
    """
    Utility Factory
    """

    class Meta:
        model = Utility

    # Using bank number. We could change this if we could fake a more suitable fake
    model_type = factory.Iterator(PropertyUtilityType.objects.all())
    description = factory.LazyAttribute(lambda o: fake.sentence())

    connected_property = factory.SubFactory(
        "crea_parser.tests.factories.property.PropertyFactory", utility=None
    )
