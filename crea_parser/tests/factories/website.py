from random import randint

import factory
from crea_parser.models import Website
from faker import Faker

fake = Faker()


class AgentWebsiteFactory(factory.django.DjangoModelFactory):
    """
    Website Factory
    """

    class Meta:
        model = Website

    text = factory.LazyAttribute(lambda o: fake.url())
    # Currently returns business, if other attributes is found
    # add more type
    contact_type = factory.LazyAttribute(lambda o: "Business")

    agent = factory.SubFactory(
        "crea_parser.tests.factories.agent.AgentFactory", website=None
    )
    office = None

    @factory.post_generation
    def WebsiteType(self, create, website, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        # If no web type is passed, create random web type
        if not website:
            website = randint(1, 2)
            if website == 1:
                website = ""
            elif website == 2:
                website = "Website"

        if website:
            # A list of web type were passed in, use them
            self.WebsiteType = website


class OfficeWebsiteFactory(factory.django.DjangoModelFactory):
    """
    Website Factory
    """

    class Meta:
        model = Website

    text = factory.LazyAttribute(lambda o: fake.url())
    # Currently returns business, if other attributes is found
    # add more type
    contact_type = factory.LazyAttribute(lambda o: "Business")

    agent = None
    office = factory.SubFactory(
        "crea_parser.tests.factories.office_details.OfficeDetailsFactory", website=None
    )

    @factory.post_generation
    def WebsiteType(self, create, website, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        # If no web type is passed, create random web type
        if not website:
            website = randint(1, 2)
            if website == 1:
                website = ""
            elif website == 2:
                website = "Website"

        if website:
            # A list of web type were passed in, use them
            self.WebsiteType = website
