import factory
from crea_parser.models import AlternateURL
from faker import Faker

fake = Faker()


class AlternateUrlFactory(factory.django.DjangoModelFactory):
    """
    Alternate Url Factory
    """

    class Meta:
        model = AlternateURL

    brochure_link = factory.LazyAttribute(lambda o: fake.url())
    map_link = factory.LazyAttribute(lambda o: fake.url())
    photo_link = factory.LazyAttribute(lambda o: fake.url())
    sound_link = factory.LazyAttribute(lambda o: fake.url())
    video_link = factory.LazyAttribute(lambda o: fake.url())
    connected_property = factory.SubFactory(
        "crea_parser.tests.factories.property.PropertyFactory", alternate_url=None
    )
