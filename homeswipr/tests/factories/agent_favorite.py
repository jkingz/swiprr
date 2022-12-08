import factory
from crea_parser.tests.factories.agent import AgentFactory
from faker import Faker
from homeswipr.models import AgentFavorite
from users.tests.factories.user import UserFactory

fake = Faker()


class AgentFavoriteFactory(factory.django.DjangoModelFactory):
    """
    Agent Favorite Factory
    """

    class Meta:
        model = AgentFavorite

    user = factory.SubFactory(UserFactory)
    favorited_agent = factory.SubFactory(AgentFactory)
