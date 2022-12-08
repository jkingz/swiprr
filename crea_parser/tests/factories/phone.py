from random import randint

import factory
from crea_parser.models import Phone
from faker import Faker

fake = Faker()


class AgentPhoneFactory(factory.django.DjangoModelFactory):
    """
    Phone Factory
    """

    class Meta:
        model = Phone

    text = factory.LazyAttribute(lambda o: fake.phone_number())
    # Currently always returns business on crea parser
    contact_type = factory.LazyAttribute(lambda o: "Business")
    agent = factory.SubFactory(
        "crea_parser.tests.factories.agent.AgentFactory", phone=None
    )
    office = None

    @factory.post_generation
    def phone_type(self, create, phone_type, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        # If no phone type is passed, create random phone type
        if not phone_type:
            phone_type = randint(1, 3)
            if phone_type == 1:
                phone_type = "Toll Fee"
            elif phone_type == 2:
                phone_type = "Telephone"
            elif phone_type == 3:
                phone_type = "Fax"

        if phone_type:
            # A list of phone type were passed in, use them
            self.phone_type = phone_type


class OfficePhoneFactory(factory.django.DjangoModelFactory):
    """
    Phone Factory
    """

    class Meta:
        model = Phone

    text = factory.LazyAttribute(lambda o: fake.phone_number())
    # Currently always returns business on crea parser
    contact_type = factory.LazyAttribute(lambda o: "Business")
    office = factory.SubFactory(
        "crea_parser.tests.factories.office_details.OfficeDetailsFactory", phone=None
    )
    agent = None

    @factory.post_generation
    def phone_type(self, create, phone_type, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        # If no phone type is passed, create random phone type
        if not phone_type:
            phone_type = randint(1, 3)
            if phone_type == 1:
                phone_type = "Toll Fee"
            elif phone_type == 2:
                phone_type = "Telephone"
            elif phone_type == 3:
                phone_type = "Fax"

        if phone_type:
            # A list of phone type were passed in, use them
            self.phone_type = phone_type
