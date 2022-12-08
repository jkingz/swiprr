from random import randint

import factory
from crea_parser.tests.utils import (
    produce_list_of_owner_ship_type_ids,
    produce_list_of_parking_type_ids,
)
from django.utils import timezone
from faker import Faker
from homeswipr.models import UserSavedSearch
from users.tests.factories.user import UserFactory

fake = Faker()


class UserSavedSearchFactory(factory.django.DjangoModelFactory):
    """
    User Saved Search Factory
    """

    class Meta:
        model = UserSavedSearch

    user = factory.SubFactory(UserFactory)
    title = factory.LazyAttribute(lambda o: fake.word())
    # # General text search that hits the a lot of fields
    search_text = factory.LazyAttribute(lambda o: fake.word())
    # # The price boundary for the search
    lower_boundary_price_range = factory.LazyAttribute(
        lambda o: fake.pydecimal(right_digits=2, max_value=100000000000)
    )
    upper_boundary_price_range = factory.LazyAttribute(
        lambda o: fake.pydecimal(right_digits=2, max_value=100000000000)
    )

    least_amount_of_bedroom = factory.LazyAttribute(lambda o: randint(0, 10))
    least_amount_of_bathroom = factory.LazyAttribute(lambda o: randint(0, 10))

    # # Store these into a list field for more convenience
    # # These should be fully supported by postgres
    ownership_type_ids = factory.LazyAttribute(
        lambda o: produce_list_of_owner_ship_type_ids()
    )
    transaction_type_id = factory.LazyAttribute(lambda o: randint(1, 4))
    parking_type_ids = factory.LazyAttribute(
        lambda o: produce_list_of_parking_type_ids()
    )

    community_search_text = factory.LazyAttribute(lambda o: fake.word())

    has_video = factory.LazyAttribute(lambda o: fake.pybool())

    from_creation_date = factory.LazyAttribute(
        lambda o: fake.past_datetime(tzinfo=timezone.get_current_timezone())
    )
    until_creation_date = factory.LazyAttribute(
        lambda o: fake.past_datetime(tzinfo=timezone.get_current_timezone())
    )
    from_listing_contract_date = factory.LazyAttribute(
        lambda o: fake.past_datetime(tzinfo=timezone.get_current_timezone())
    )
    until_listing_contract_date = factory.LazyAttribute(
        lambda o: fake.past_datetime(tzinfo=timezone.get_current_timezone())
    )
    last_checked_date = factory.LazyAttribute(
        lambda o: fake.past_datetime(tzinfo=timezone.get_current_timezone())
    )
    created_by = factory.SubFactory(UserFactory)
