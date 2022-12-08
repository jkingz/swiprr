from collections import OrderedDict

import factory
from crea_parser.models import Address
from faker import Faker

locales = OrderedDict(
    [
        ("en_CA", 1),
    ]
)

fake = Faker(locales)


class PropertyAddressFactory(factory.django.DjangoModelFactory):
    """
    Property Address Factory
    """

    class Meta:
        model = Address

    street_address = factory.LazyAttribute(lambda o: fake.street_address())
    address_line1 = factory.LazyAttribute(lambda o: fake.address())
    address_line2 = factory.LazyAttribute(lambda o: fake.address())
    street_number = factory.LazyAttribute(lambda o: fake.building_number())
    street_direction_prefix = factory.LazyAttribute(lambda o: fake.word())
    street_name = factory.LazyAttribute(lambda o: fake.street_name())
    street_suffix = factory.LazyAttribute(lambda o: fake.street_suffix())
    street_direction_suffix = factory.LazyAttribute(lambda o: fake.word())
    unit_number = factory.LazyAttribute(lambda o: fake.building_number())
    box_number = factory.LazyAttribute(lambda o: fake.building_number())
    city = factory.LazyAttribute(lambda o: fake.city())
    province = factory.LazyAttribute(lambda o: fake["en_CA"].province())
    postal_code = factory.LazyAttribute(lambda o: fake.postcode())
    country = factory.LazyAttribute(lambda o: fake.country())
    additional_street_info = factory.LazyAttribute(lambda o: fake.sentence())
    community_name = factory.LazyAttribute(lambda o: fake.word())
    neighbourhood = factory.LazyAttribute(lambda o: fake.word())
    subdivision = factory.LazyAttribute(lambda o: fake.sentence())
    connected_property = factory.SubFactory(
        "crea_parser.tests.factories.property.PropertyFactory", address=None
    )

    # If we need tests for office and agent
    # create another class that connects to this two instead
    office = None
    agent = None


class AgentAddressFactory(factory.django.DjangoModelFactory):
    """
    agent Address Factory
    """

    class Meta:
        model = Address

    street_address = factory.LazyAttribute(lambda o: fake.street_address())
    address_line1 = factory.LazyAttribute(lambda o: fake.address())
    address_line2 = factory.LazyAttribute(lambda o: fake.address())
    street_number = factory.LazyAttribute(lambda o: fake.building_number())
    street_direction_prefix = factory.LazyAttribute(lambda o: fake.word())
    street_name = factory.LazyAttribute(lambda o: fake.street_name())
    street_suffix = factory.LazyAttribute(lambda o: fake.street_suffix())
    street_direction_suffix = factory.LazyAttribute(lambda o: fake.word())
    unit_number = factory.LazyAttribute(lambda o: fake.building_number())
    box_number = factory.LazyAttribute(lambda o: fake.building_number())
    city = factory.LazyAttribute(lambda o: fake.city())
    province = factory.LazyAttribute(lambda o: fake["en_CA"].province())
    postal_code = factory.LazyAttribute(lambda o: fake.postcode())
    country = factory.LazyAttribute(lambda o: fake.country())
    additional_street_info = factory.LazyAttribute(lambda o: fake.sentence())
    community_name = factory.LazyAttribute(lambda o: fake.word())
    neighbourhood = factory.LazyAttribute(lambda o: fake.word())
    subdivision = factory.LazyAttribute(lambda o: fake.sentence())

    office = None
    connected_property = None
    agent = factory.SubFactory(
        "crea_parser.tests.factories.agent.AgentFactory", address=None
    )


class OfficeAddressFactory(factory.django.DjangoModelFactory):
    """
    office Address Factory
    """

    class Meta:
        model = Address

    street_address = factory.LazyAttribute(lambda o: fake.street_address())
    address_line1 = factory.LazyAttribute(lambda o: fake.address())
    address_line2 = factory.LazyAttribute(lambda o: fake.address())
    street_number = factory.LazyAttribute(lambda o: fake.building_number())
    street_direction_prefix = factory.LazyAttribute(lambda o: fake.word())
    street_name = factory.LazyAttribute(lambda o: fake.street_name())
    street_suffix = factory.LazyAttribute(lambda o: fake.street_suffix())
    street_direction_suffix = factory.LazyAttribute(lambda o: fake.word())
    unit_number = factory.LazyAttribute(lambda o: fake.building_number())
    box_number = factory.LazyAttribute(lambda o: fake.building_number())
    city = factory.LazyAttribute(lambda o: fake.city())
    province = factory.LazyAttribute(lambda o: fake["en_CA"].province())
    postal_code = factory.LazyAttribute(lambda o: fake.postcode())
    country = factory.LazyAttribute(lambda o: fake.country())
    additional_street_info = factory.LazyAttribute(lambda o: fake.sentence())
    community_name = factory.LazyAttribute(lambda o: fake.word())
    neighbourhood = factory.LazyAttribute(lambda o: fake.word())
    subdivision = factory.LazyAttribute(lambda o: fake.sentence())

    office = factory.SubFactory(
        "crea_parser.tests.factories.office_details.OfficeDetailsFactory", address=None
    )
    connected_property = None
    agent = None
