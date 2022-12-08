import factory
from users.models import Referral
from users.tests.factories.user import UserFactory


class ReferralFactory(factory.django.DjangoModelFactory):

    invited_user = factory.SubFactory(UserFactory)
    referred_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Referral
