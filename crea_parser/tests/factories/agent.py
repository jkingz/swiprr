import factory
from crea_parser.models import AgentDetails
from crea_parser.tests.factories.address import AgentAddressFactory
from crea_parser.tests.factories.office_details import OfficeDetailsFactory
from crea_parser.tests.factories.phone import AgentPhoneFactory
from crea_parser.tests.factories.website import AgentWebsiteFactory
from django.utils import timezone
from faker import Faker

fake = Faker()


class AgentFactory(factory.django.DjangoModelFactory):
    """
    Agent Factory
    """

    class Meta:
        model = AgentDetails

    # Using bank number. We could change this if we could fake a more suitable fake
    ddf_id = factory.LazyAttribute(lambda o: fake.bban())
    name = factory.LazyAttribute(lambda o: fake.name())
    last_updated = factory.LazyAttribute(
        lambda o: fake.past_datetime(tzinfo=timezone.get_current_timezone())
    )
    position = factory.LazyAttribute(lambda o: fake.job())
    connected_property = factory.SubFactory(
        "crea_parser.tests.factories.property.PropertyFactory", agent=None
    )

    office = factory.RelatedFactory(OfficeDetailsFactory, factory_related_name="agent")

    phone = factory.RelatedFactory(AgentPhoneFactory, factory_related_name="agent")

    address = factory.RelatedFactory(AgentAddressFactory, factory_related_name="agent")

    website = factory.RelatedFactory(AgentWebsiteFactory, factory_related_name="agent")
