import factory
from crea_parser.tests.factories.property import PropertyFactory
from faker import Faker
from homeswipr.models import PropertyFavorite
from users.tests.factories.user import UserFactory

fake = Faker()


class PropertyFavoriteFactory(factory.django.DjangoModelFactory):
    """
    Property Favorite Factory
    """

    class Meta:
        model = PropertyFavorite

    user = factory.SubFactory(UserFactory)
    favorited_property = factory.SubFactory(PropertyFactory)
