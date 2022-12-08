from collections import OrderedDict
from random import randint

import factory
from crea_parser.models import Room
from crea_parser.submodels.metadata import PropertyRoomType, PropertyMeasureUnit

from faker import Faker

locales = OrderedDict(
    [
        ("en_PH", 1),
    ]
)

fake = Faker(locales)


class RoomFactory(factory.django.DjangoModelFactory):
    """
    Room Factory
    """

    class Meta:
        model = Room

    # Find a better fake for the type
    model_type = factory.Iterator(PropertyRoomType.active_objects.all())

    width = factory.LazyAttribute(lambda o: randint(1, 100))
    width_unit = factory.Iterator(PropertyMeasureUnit.active_objects.all())
    length = factory.LazyAttribute(lambda o: randint(1, 100))
    length_unit = factory.Iterator(PropertyMeasureUnit.active_objects.all())

    connected_property = factory.SubFactory(
        "crea_parser.tests.factories.property.PropertyFactory", room=None
    )

    @factory.post_generation
    def Dimension(self, create, Dimension, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if Dimension:
            self.Dimension = Dimension
        else:
            self.Dimension = f"{self.length}{self.length_unit} x {self.width}{self.width_unit}"
