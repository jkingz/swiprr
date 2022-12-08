import factory
from crea_parser.models import OfficeDetails
from crea_parser.tests.factories.phone import OfficePhoneFactory
from crea_parser.tests.factories.website import OfficeWebsiteFactory
from django.utils import timezone
from faker import Faker

fake = Faker()


class OfficeDetailsFactory(factory.django.DjangoModelFactory):
    """
    Office Details Factory
    """

    class Meta:
        model = OfficeDetails

    # Using bank number. We could change this if we could fake a more suitable fake
    ddf_id = factory.LazyAttribute(lambda o: fake.bban())
    name = factory.LazyAttribute(lambda o: fake.company())

    agent = factory.SubFactory(
        "crea_parser.tests.factories.agent.AgentFactory", office=None
    )

    phone = factory.RelatedFactory(OfficePhoneFactory, factory_related_name="office")

    website = factory.RelatedFactory(
        OfficeWebsiteFactory, factory_related_name="office"
    )
