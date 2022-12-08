import uuid
from datetime import timedelta
from random import randint

from crea_parser.models import Parking, PropertyInfo
from crea_parser.tests.factories.parking import ParkingFactory
from crea_parser.tests.factories.property import PropertyFactory
from crea_parser.submodels.metadata import PropertyParkingType, PropertyTransactionType, PropertyOwnershipType, PropertyPropertyType
from core.shortcuts import get_object_or_None
from django.contrib.gis.geos import Point
from django.urls import reverse
from django.utils import timezone
from faker import Faker
from homeswipr.models import UserSavedSearch
from homeswipr.tests.factories.user_saved_search import UserSavedSearchFactory
from rest_framework import status
from users.models import UserHistory
from users.tests.factories.user_history import UserPropertyHistoryFactory

from .base_app_test import CoreBaseTest


class PropertyCoreBaseTest(CoreBaseTest):
    def setUp(self, *args, **kwargs):
        # Should never be included in our results
        PropertyFactory(is_active=False)
        return super().setUp(*args, **kwargs)


class PropertyTestCases(PropertyCoreBaseTest):
    """
    Property Test Cases
    """

    base_name = "property"
    fake = Faker()

    # Our testing data should not go this id number
    invalid_pk = 999999

    def setUp(self, *args, **kwargs):
        return super().setUp(*args, **kwargs)

    def test_get_property_list_succeeds(self, *args, **kwargs):
        self.login_active_user()

        # The ownership type Agriculture and Vacant land is not needed
        # We test right here, if invalid is not ownership type is excluded
        response = self.client.get(reverse(self.get_list_url()), {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_list_without_excluded_type_succeeds(self, *args, **kwargs):

        PropertyFactory()

        self.login_active_user()

        excluded_property_type = PropertyPropertyType.active_objects.filter(include_on_base_homeswipr_filter=False)

        for entry in excluded_property_type:
            PropertyFactory(
                property_info__property_type=entry
            )

        response = self.client.get(reverse(self.get_list_url()), {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["mls_matched"], False)
        self.assertEqual(response.data["count"], 1)

    def test_get_property_list_with_uauthenticated_user_succeeds(self, *args, **kwargs):
        # Permission deny
        response = self.client.get(reverse(self.get_list_url()), {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_property_list_with_saved_search_succeeds_and_checked_date_changes(
        self, *args, **kwargs
    ):

        self.login_active_user()

        user_saved_search = UserSavedSearchFactory(user=self.active_user)
        old_last_checked_date = user_saved_search.last_checked_date

        response = self.client.get(
            reverse(self.get_list_url()), data={"saved_search_pk": user_saved_search.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        new_saved_search = UserSavedSearch.active_objects.get(pk=user_saved_search.pk)
        self.assertNotEqual(new_saved_search.last_checked_date, old_last_checked_date)

    def test_get_property_list_with_saved_search_with_other_user_fails(
        self, *args, **kwargs
    ):

        self.login_other_user()

        user_saved_search = UserSavedSearchFactory(user=self.active_user)

        response = self.client.get(
            reverse(self.get_list_url()), data={"saved_search_pk": user_saved_search.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_property_list_with_saved_search_with_unauth_user_fails(
        self, *args, **kwargs
    ):

        user_saved_search = UserSavedSearchFactory(user=self.active_user)

        response = self.client.get(
            reverse(self.get_list_url()), data={"saved_search_pk": user_saved_search.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_property_list_with_saved_search_search_text_succeeds(
        self, *args, **kwargs
    ):
        self.login_active_user()

        # Not a address but this should be able to search check the property list properly
        unique_string = str(uuid.uuid4())

        user_saved_search = UserSavedSearchFactory(
            user=self.active_user,
            search_text=unique_string,
            lower_boundary_price_range=None,
            upper_boundary_price_range=None,
            least_amount_of_bedroom=None,
            least_amount_of_bathroom=None,
            ownership_type_ids=None,
            transaction_type_id=None,
            parking_type_ids=None,
            community_search_text="",
            has_video=None,
            from_creation_date=None,
            until_creation_date=None,
            from_listing_contract_date=None,
            until_listing_contract_date=None,
            last_checked_date=None,
        )

        PropertyFactory(full_address=unique_string)
        PropertyFactory(unit_number=unique_string)
        PropertyFactory(street_number=unique_string)
        PropertyFactory(street_name=unique_string)
        PropertyFactory(postal_code=unique_string)

        PropertyFactory(address__address_line1=unique_string)
        PropertyFactory(address__address_line2=unique_string)
        PropertyFactory(address__street_number=unique_string)
        PropertyFactory(address__street_direction_prefix=unique_string)
        PropertyFactory(address__street_name=unique_string)
        PropertyFactory(address__street_suffix=unique_string)
        PropertyFactory(address__street_direction_suffix=unique_string)
        PropertyFactory(address__unit_number=unique_string)
        PropertyFactory(address__box_number=unique_string)
        PropertyFactory(address__city=unique_string)
        PropertyFactory(address__province=unique_string)
        PropertyFactory(address__postal_code=unique_string)

        response = self.client.get(
            reverse(self.get_list_url()), data={"saved_search_pk": user_saved_search.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 17)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_list_with_general_text_specific_search_string_succeeds(
        self, *args, **kwargs
    ):
        self.login_active_user()
        # Not a address but this should be able to search check the property list properly
        # This should avoid things like producing an address with faker that's the same with self
        unique_string = str(uuid.uuid4())

        PropertyFactory(full_address=unique_string)
        PropertyFactory(unit_number=unique_string)
        PropertyFactory(street_number=unique_string)
        PropertyFactory(street_name=unique_string)
        PropertyFactory(postal_code=unique_string)

        PropertyFactory(address__address_line1=unique_string)
        PropertyFactory(address__address_line2=unique_string)
        PropertyFactory(address__street_number=unique_string)
        PropertyFactory(address__street_direction_prefix=unique_string)
        PropertyFactory(address__street_name=unique_string)
        PropertyFactory(address__street_suffix=unique_string)
        PropertyFactory(address__street_direction_suffix=unique_string)
        PropertyFactory(address__unit_number=unique_string)
        PropertyFactory(address__box_number=unique_string)
        PropertyFactory(address__city=unique_string)
        PropertyFactory(address__province=unique_string)
        PropertyFactory(address__postal_code=unique_string)

        response = self.client.get(
            reverse(self.get_list_url()), data={"search_text": unique_string}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 17)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_list_with_community_neighborhood_subdivision_search_string_succeeds(
        self, *args, **kwargs
    ):

        self.login_active_user()

        unique_string = str(uuid.uuid4())

        PropertyFactory(address__community_name=unique_string)
        PropertyFactory(address__neighbourhood=unique_string)
        PropertyFactory(address__subdivision=unique_string)

        response = self.client.get(
            reverse(self.get_list_url()), data={"community_search_text": unique_string}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_list_community_neighborhood_subdivision_from_saved_search_succeeds(
        self, *args, **kwargs
    ):

        self.login_active_user()

        unique_string = str(uuid.uuid4())

        PropertyFactory(address__community_name=unique_string)
        PropertyFactory(address__neighbourhood=unique_string)
        PropertyFactory(address__subdivision=unique_string)

        user_saved_search = UserSavedSearchFactory(
            user=self.active_user,
            search_text="",
            lower_boundary_price_range=None,
            upper_boundary_price_range=None,
            least_amount_of_bedroom=None,
            least_amount_of_bathroom=None,
            ownership_type_ids=None,
            transaction_type_id=None,
            parking_type_ids=None,
            community_search_text=unique_string,
            has_video=None,
            from_creation_date=None,
            until_creation_date=None,
            from_listing_contract_date=None,
            until_listing_contract_date=None,
            last_checked_date=None,
        )

        response = self.client.get(
            reverse(self.get_list_url()), data={"saved_search_pk": user_saved_search.pk}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_list_with_range_filter_succeeds(self, *args, **kwargs):

        self.login_active_user()
        property_one = PropertyFactory()
        price = property_one.Info.price

        # Override lease price
        property_one.Lease = 0
        property_one.save()

        upper_boundary_price_range = self.fake.pydecimal(
            right_digits=2, min_value=int(price), max_value=100000000000
        )
        lower_boundary_price_range = self.fake.pydecimal(
            right_digits=2, min_value=0, max_value=int(price)
        )

        response = self.client.get(
            reverse(self.get_list_url()),
            data={
                "lower_boundary_price_range": lower_boundary_price_range,
                "upper_boundary_price_range": upper_boundary_price_range,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_list_with_range_filter_on_rent_succeeds(
        self, *args, **kwargs
    ):

        self.login_active_user()
        property_one = PropertyFactory()
        price = property_one.Info.lease

        # Override lease price
        property_one.price = 0
        property_one.save()

        upper_boundary_price_range = self.fake.pydecimal(
            right_digits=2, min_value=int(price), max_value=100000000000
        )
        lower_boundary_price_range = self.fake.pydecimal(
            right_digits=2, min_value=0, max_value=int(price)
        )

        response = self.client.get(
            reverse(self.get_list_url()),
            data={
                "lower_boundary_price_range": lower_boundary_price_range,
                "upper_boundary_price_range": upper_boundary_price_range,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_list_with_empty_string_as_filter_succeeds(
        self, *args, **kwargs
    ):

        PropertyFactory()

        self.login_active_user()
        upper_boundary_price_range = ""
        lower_boundary_price_range = ""

        response = self.client.get(
            reverse(self.get_list_url()),
            data={
                "lower_boundary_price_range": lower_boundary_price_range,
                "upper_boundary_price_range": upper_boundary_price_range,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_list_with_range_filter_from_saved_search_succeeds(
        self, *args, **kwargs
    ):

        self.login_active_user()
        property_one = PropertyFactory()
        price = property_one.Info.price

        user_saved_search = UserSavedSearchFactory(
            user=self.active_user,
            search_text="",
            lower_boundary_price_range=self.fake.pydecimal(
                right_digits=2, min_value=0, max_value=int(price)
            ),
            upper_boundary_price_range=self.fake.pydecimal(
                right_digits=2, min_value=int(price), max_value=100000000000
            ),
            least_amount_of_bedroom=None,
            least_amount_of_bathroom=None,
            ownership_type_ids=None,
            transaction_type_id=None,
            parking_type_ids=None,
            community_search_text="",
            has_video=None,
            from_creation_date=None,
            until_creation_date=None,
            from_listing_contract_date=None,
            until_listing_contract_date=None,
            last_checked_date=None,
        )

        response = self.client.get(
            reverse(self.get_list_url()), data={"saved_search_pk": user_saved_search.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_list_with_invalid_format_for_range_filter_fails(
        self, *args, **kwargs
    ):

        self.login_active_user()
        property_one = PropertyFactory()
        property_one.Info.price
        upper_boundary_price_range = self.fake.word()
        lower_boundary_price_range = self.fake.word()

        response = self.client.get(
            reverse(self.get_list_url()),
            data={
                "lower_boundary_price_range": lower_boundary_price_range,
                "upper_boundary_price_range": upper_boundary_price_range,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_property_with_least_amount_of_bathroom_succeeds(self, *args, **kwargs):

        self.login_active_user()

        property_one = PropertyFactory()
        bathroom_count = property_one.Building.bathroom_total
        at_least_bathroom_count = randint(0, bathroom_count)

        response = self.client.get(
            reverse(self.get_list_url()),
            data={"least_amount_of_bathroom": at_least_bathroom_count},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_with_least_amount_of_bathroom_using_saved_search_succeeds(
        self, *args, **kwargs
    ):

        self.login_active_user()

        property_one = PropertyFactory()
        bathroom_count = property_one.Building.bathroom_total
        user_saved_search = UserSavedSearchFactory(
            user=self.active_user,
            search_text="",
            lower_boundary_price_range=None,
            upper_boundary_price_range=None,
            least_amount_of_bedroom=None,
            least_amount_of_bathroom=randint(0, bathroom_count),
            ownership_type_ids=None,
            transaction_type_id=None,
            parking_type_ids=None,
            community_search_text="",
            has_video=None,
            from_creation_date=None,
            until_creation_date=None,
            from_listing_contract_date=None,
            until_listing_contract_date=None,
            last_checked_date=None,
        )

        response = self.client.get(
            reverse(self.get_list_url()), data={"saved_search_pk": user_saved_search.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_with_invalid_format_for_least_amount_of_bathroom_fails(
        self, *args, **kwargs
    ):

        self.login_active_user()

        property_one = PropertyFactory()
        property_one.Building.bathroom_total
        at_least_bathroom_count = self.fake.word()

        response = self.client.get(
            reverse(self.get_list_url()),
            data={"least_amount_of_bathroom": at_least_bathroom_count},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_property_with_least_amount_of_bedroom_succeeds(self, *args, **kwargs):

        self.login_active_user()

        property_one = PropertyFactory()
        bedroom_count = property_one.Building.bedrooms_total
        at_least_bedroom_count = randint(0, bedroom_count)

        response = self.client.get(
            reverse(self.get_list_url()),
            data={"least_amount_of_bedroom": at_least_bedroom_count},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_with_least_amount_of_bedroom_using_saved_search_succeeds(
        self, *args, **kwargs
    ):

        self.login_active_user()

        property_one = PropertyFactory()
        bedroom_count = property_one.Building.bedrooms_total

        user_saved_search = UserSavedSearchFactory(
            user=self.active_user,
            search_text="",
            lower_boundary_price_range=None,
            upper_boundary_price_range=None,
            least_amount_of_bedroom=randint(0, bedroom_count),
            least_amount_of_bathroom=None,
            ownership_type_ids=None,
            transaction_type_id=None,
            parking_type_ids=None,
            community_search_text="",
            has_video=None,
            from_creation_date=None,
            until_creation_date=None,
            from_listing_contract_date=None,
            until_listing_contract_date=None,
            last_checked_date=None,
        )

        response = self.client.get(
            reverse(self.get_list_url()), data={"saved_search_pk": user_saved_search.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_with_invalid_format_for_least_amount_of_bedroom_fails(
        self, *args, **kwargs
    ):

        self.login_active_user()

        property_one = PropertyFactory()
        property_one.Building.bedrooms_total
        at_least_bedroom_count = self.fake.word()

        response = self.client.get(
            reverse(self.get_list_url()),
            data={"least_amount_of_bedroom": at_least_bedroom_count},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_property_with_transaction_type_for_sale_succeeds(
        self, *args, **kwargs
    ):

        self.login_active_user()

        # For sale
        transaction_id = 2

        PropertyFactory(
            property_info__transaction_type=get_object_or_None(PropertyTransactionType.active_objects, metadata_entry_id=1)
        )

        PropertyFactory(
            property_info__transaction_type=get_object_or_None(PropertyTransactionType.active_objects, metadata_entry_id=2)
        )

        PropertyFactory(
            property_info__transaction_type=get_object_or_None(PropertyTransactionType.active_objects, metadata_entry_id=3)
        )

        PropertyFactory(
            property_info__transaction_type=get_object_or_None(PropertyTransactionType.active_objects, metadata_entry_id=4)
        )

        response = self.client.get(
            reverse(self.get_list_url()), data={"transaction_type_id": transaction_id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_with_transaction_type_for_rent_succeeds(
        self, *args, **kwargs
    ):

        self.login_active_user()

        # For rent
        transaction_id = 3

        PropertyFactory(
            property_info__transaction_type=get_object_or_None(PropertyTransactionType.active_objects, metadata_entry_id=1)
        )

        PropertyFactory(
            property_info__transaction_type=get_object_or_None(PropertyTransactionType.active_objects, metadata_entry_id=2)
        )

        PropertyFactory(
            property_info__transaction_type=get_object_or_None(PropertyTransactionType.active_objects, metadata_entry_id=3)
        )

        PropertyFactory(
            property_info__transaction_type=get_object_or_None(PropertyTransactionType.active_objects, metadata_entry_id=4)
        )

        response = self.client.get(
            reverse(self.get_list_url()), data={"transaction_type_id": transaction_id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_with_transaction_type_for_lease_succeeds(
        self, *args, **kwargs
    ):

        self.login_active_user()

        transaction_id = 4

        PropertyFactory(
            property_info__transaction_type=get_object_or_None(PropertyTransactionType.active_objects, metadata_entry_id=1)
        )

        PropertyFactory(
            property_info__transaction_type=get_object_or_None(PropertyTransactionType.active_objects, metadata_entry_id=2)
        )

        # ID Number 1 is for lease
        PropertyFactory(
            property_info__transaction_type=get_object_or_None(PropertyTransactionType.active_objects, metadata_entry_id=3)
        )

        PropertyFactory(
            property_info__transaction_type=get_object_or_None(PropertyTransactionType.active_objects, metadata_entry_id=4)
        )

        response = self.client.get(
            reverse(self.get_list_url()), data={"transaction_type_id": transaction_id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_with_transaction_type_for_rent_or_sale_succeeds(
        self, *args, **kwargs
    ):

        self.login_active_user()

        transaction_id = 1

        PropertyFactory(
            property_info__transaction_type=get_object_or_None(PropertyTransactionType.active_objects, metadata_entry_id=1)
        )

        PropertyFactory(
            property_info__transaction_type=get_object_or_None(PropertyTransactionType.active_objects, metadata_entry_id=2)
        )

        PropertyFactory(
            property_info__transaction_type=get_object_or_None(PropertyTransactionType.active_objects, metadata_entry_id=3)
        )

        PropertyFactory(
            property_info__transaction_type=get_object_or_None(PropertyTransactionType.active_objects, metadata_entry_id=4)
        )

        response = self.client.get(
            reverse(self.get_list_url()), data={"transaction_type_id": transaction_id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_with_transaction_type_succeeds(self, *args, **kwargs):

        self.login_active_user()

        transaction_id = randint(1, 4)

        PropertyFactory(
            property_info__transaction_type=get_object_or_None(PropertyTransactionType.active_objects, metadata_entry_id=
                transaction_id
            )
        )

        response = self.client.get(
            reverse(self.get_list_url()), data={"transaction_type_id": transaction_id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_with_transaction_type_using_saved_search_succeeds(
        self, *args, **kwargs
    ):

        self.login_active_user()

        transaction_id = randint(1, 4)

        user_saved_search = UserSavedSearchFactory(
            user=self.active_user,
            search_text="",
            lower_boundary_price_range=None,
            upper_boundary_price_range=None,
            least_amount_of_bedroom=None,
            least_amount_of_bathroom=None,
            ownership_type_ids=None,
            transaction_type_id=transaction_id,
            parking_type_ids=None,
            community_search_text="",
            has_video=None,
            from_creation_date=None,
            until_creation_date=None,
            from_listing_contract_date=None,
            until_listing_contract_date=None,
            last_checked_date=None,
        )

        PropertyFactory(
            property_info__transaction_type=get_object_or_None(PropertyTransactionType.active_objects, metadata_entry_id=
                transaction_id
            )
        )

        response = self.client.get(
            reverse(self.get_list_url()), data={"saved_search_pk": user_saved_search.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_with_ivalid_format_transaction_type_fails(
        self, *args, **kwargs
    ):

        self.login_active_user()

        transaction_id = self.fake.word()

        response = self.client.get(
            reverse(self.get_list_url()), data={"transaction_type_id": transaction_id}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_property_with_creation_date_format_succeeds(self, *args, **kwargs):

        self.login_active_user()

        property_one = PropertyFactory()
        creation_date = property_one.creation_date
        from_date = creation_date - timedelta(days=randint(0, 100))
        until_date = creation_date + timedelta(days=randint(0, 100))

        response = self.client.get(
            reverse(self.get_list_url()),
            data={"from_creation_date": from_date, "until_creation_date": until_date},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_newer_saved_search_succeeds(self, *args, **kwargs):
        self.login_active_user()

        property_one = PropertyFactory()
        creation_date = property_one.creation_date
        last_checked = creation_date - timedelta(days=randint(1, 100))

        user_saved_search = UserSavedSearchFactory(
            user=self.active_user,
            search_text="",
            lower_boundary_price_range=None,
            upper_boundary_price_range=None,
            least_amount_of_bedroom=None,
            least_amount_of_bathroom=None,
            ownership_type_ids=None,
            transaction_type_id=None,
            parking_type_ids=None,
            community_search_text="",
            has_video=None,
            from_creation_date=None,
            until_creation_date=None,
            from_listing_contract_date=None,
            until_listing_contract_date=None,
        )

        user_saved_search.last_checked_date = last_checked
        user_saved_search.save()

        PropertyFactory(creation_date=last_checked)

        response = self.client.get(
            reverse(self.get_list_url()),
            data={
                "saved_search_pk": user_saved_search.pk,
                # Frontend passes it as string on our part
                "show_only_new_ones": "true",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_with_creation_date_using_saved_search_format_succeeds(
        self, *args, **kwargs
    ):

        self.login_active_user()

        property_one = PropertyFactory()
        creation_date = property_one.creation_date
        from_date = creation_date - timedelta(days=randint(0, 100))
        until_date = creation_date + timedelta(days=randint(0, 100))

        user_saved_search = UserSavedSearchFactory(
            user=self.active_user,
            search_text="",
            lower_boundary_price_range=None,
            upper_boundary_price_range=None,
            least_amount_of_bedroom=None,
            least_amount_of_bathroom=None,
            ownership_type_ids=None,
            transaction_type_id=None,
            parking_type_ids=None,
            community_search_text="",
            has_video=None,
            from_creation_date=from_date,
            until_creation_date=until_date,
            from_listing_contract_date=None,
            until_listing_contract_date=None,
            last_checked_date=None,
        )

        response = self.client.get(
            reverse(self.get_list_url()), data={"saved_search_pk": user_saved_search.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_with_creation_date_invalid_format_fails(
        self, *args, **kwargs
    ):

        self.login_active_user()

        property_one = PropertyFactory()
        property_one.creation_date
        from_date = self.fake.word()
        until_date = self.fake.word()

        response = self.client.get(
            reverse(self.get_list_url()),
            data={"from_creation_date": from_date, "until_creation_date": until_date},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_property_with_reverse_creation_date_filter_is_empty_but_succeeds(
        self, *args, **kwargs
    ):

        self.login_active_user()

        property_one = PropertyFactory()
        creation_date = property_one.creation_date
        from_date = creation_date + timedelta(days=randint(0, 100))
        until_date = creation_date - timedelta(days=randint(0, 100))

        response = self.client.get(
            reverse(self.get_list_url()),
            data={"from_creation_date": from_date, "until_creation_date": until_date},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_with_listing_date_format_succeeds(self, *args, **kwargs):

        self.login_active_user()

        property_one = PropertyFactory()
        listing_date = property_one.Info.listing_contract_date
        from_date = listing_date - timedelta(days=randint(0, 100))
        until_date = listing_date + timedelta(days=randint(0, 100))

        response = self.client.get(
            reverse(self.get_list_url()),
            data={
                "from_listing_contract_date": from_date,
                "until_listing_contract_date": until_date,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_with_listing_date_using_saved_search_format_succeeds(
        self, *args, **kwargs
    ):

        self.login_active_user()

        property_one = PropertyFactory()
        listing_date = property_one.Info.listing_contract_date
        from_date = listing_date - timedelta(days=randint(0, 100))
        until_date = listing_date + timedelta(days=randint(0, 100))

        user_saved_search = UserSavedSearchFactory(
            user=self.active_user,
            search_text="",
            lower_boundary_price_range=None,
            upper_boundary_price_range=None,
            least_amount_of_bedroom=None,
            least_amount_of_bathroom=None,
            ownership_type_ids=None,
            transaction_type_id=None,
            parking_type_ids=None,
            community_search_text="",
            has_video=None,
            from_creation_date=None,
            until_creation_date=None,
            from_listing_contract_date=from_date,
            until_listing_contract_date=until_date,
            last_checked_date=None,
        )

        response = self.client.get(
            reverse(self.get_list_url()), data={"saved_search_pk": user_saved_search.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_with_reverse_from_listing_date_format_is_empty_but_succeeds(
        self, *args, **kwargs
    ):

        self.login_active_user()

        property_one = PropertyFactory()
        listing_date = property_one.Info.listing_contract_date
        from_date = listing_date + timedelta(days=randint(0, 100))
        until_date = listing_date - timedelta(days=randint(0, 100))
        response = self.client.get(
            reverse(self.get_list_url()),
            data={
                "from_listing_contract_date": from_date,
                "until_listing_contract_date": until_date,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_with_invalid_string_listing_date_format_fails(
        self, *args, **kwargs
    ):

        self.login_active_user()

        property_one = PropertyFactory()
        property_one.Info.listing_contract_date
        from_date = self.fake.word()
        until_date = self.fake.word()

        response = self.client.get(
            reverse(self.get_list_url()),
            data={
                "from_listing_contract_date": from_date,
                "until_listing_contract_date": until_date,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_property_with_has_video_succeeds(self, *args, **kwargs):

        self.login_active_user()

        PropertyFactory()
        # Add an empty one. since property one always has a video url
        PropertyFactory(alternate_url__video_link="")
        # Since the frontend passes as string that is defined as "true"
        has_video = "true"

        response = self.client.get(
            reverse(self.get_list_url()), data={"has_video": has_video}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # There should be a single equal, since currently we always
        # put a video link property one
        self.assertEqual(response.data["count"], 1)

    def test_get_property_with_has_video_using_saved_search_succeeds(
        self, *args, **kwargs
    ):

        self.login_active_user()

        PropertyFactory()
        # Add an empty one. since property one always has a video url
        PropertyFactory(alternate_url__video_link="")

        user_saved_search = UserSavedSearchFactory(
            user=self.active_user,
            search_text="",
            lower_boundary_price_range=None,
            upper_boundary_price_range=None,
            least_amount_of_bedroom=None,
            least_amount_of_bathroom=None,
            ownership_type_ids=None,
            transaction_type_id=None,
            parking_type_ids=None,
            community_search_text="",
            has_video=True,
            from_creation_date=None,
            until_creation_date=None,
            from_listing_contract_date=None,
            until_listing_contract_date=None,
            last_checked_date=None,
        )

        response = self.client.get(
            reverse(self.get_list_url()), data={"saved_search_pk": user_saved_search.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_with_filter_parking_using_saved_search_succeeds(
        self, *args, **kwargs
    ):

        PropertyFactory()

        self.login_active_user()

        parking_list = PropertyParkingType.active_objects.all().values_list("metadata_entry_id", flat=True)

        type_casted_parking_list = []

        for parking_id in parking_list:
            type_casted_parking_list.append(parking_id)
            ParkingFactory(name=get_object_or_None(PropertyParkingType.active_objects, metadata_entry_id=parking_id))

        user_saved_search = UserSavedSearchFactory(
            user=self.active_user,
            search_text="",
            lower_boundary_price_range=None,
            upper_boundary_price_range=None,
            least_amount_of_bedroom=None,
            least_amount_of_bathroom=None,
            ownership_type_ids=None,
            transaction_type_id=None,
            parking_type_ids=type_casted_parking_list,
            community_search_text="",
            has_video=None,
            from_creation_date=None,
            until_creation_date=None,
            from_listing_contract_date=None,
            until_listing_contract_date=None,
            last_checked_date=None,
        )

        response = self.client.get(
            reverse(self.get_list_url()), data={"saved_search_pk": user_saved_search.pk}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Count the setup too, which make this 38 + 1
        self.assertEqual(response.data["count"], 39)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_with_filter_parking_and_valid_format_succeeds(
        self, *args, **kwargs
    ):

        PropertyFactory()

        self.login_active_user()

        parking_list = PropertyParkingType.active_objects.all().values_list("metadata_entry_id", flat=True)

        type_casted_parking_list = []

        for parking_id in parking_list:
            type_casted_parking_list.append(parking_id)
            ParkingFactory(name=get_object_or_None(PropertyParkingType.active_objects, metadata_entry_id=parking_id))

        response = self.client.get(
            reverse(self.get_list_url()), data={"parking_type_ids[]": parking_list}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Count the setup too, which make this 38 + 1
        self.assertEqual(response.data["count"], 39)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_with_fitler_parking_and_invalid_format_fails(
        self, *args, **kwargs
    ):

        self.login_active_user()

        parking_list = [self.fake.word(), self.fake.word()]

        response = self.client.get(
            reverse(self.get_list_url()), data={"parking_type_ids[]": parking_list}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_property_owner_type_by_saved_search_succeeds(self, *args, **kwargs):

        PropertyFactory()

        self.login_active_user()

        ownership_list = PropertyOwnershipType.active_objects.all().values_list("metadata_entry_id", flat=True)

        type_casted_ownership_list = []

        for ownership_type_id in ownership_list:
            type_casted_ownership_list.append(ownership_type_id)
            PropertyFactory(
                property_info__ownership_type=get_object_or_None(PropertyOwnershipType.active_objects, metadata_entry_id=ownership_type_id)
            )


        user_saved_search = UserSavedSearchFactory(
            user=self.active_user,
            search_text="",
            lower_boundary_price_range=None,
            upper_boundary_price_range=None,
            least_amount_of_bedroom=None,
            least_amount_of_bathroom=None,
            ownership_type_ids=type_casted_ownership_list,
            transaction_type_id=None,
            parking_type_ids=None,
            community_search_text="",
            has_video=None,
            from_creation_date=None,
            until_creation_date=None,
            from_listing_contract_date=None,
            until_listing_contract_date=None,
            last_checked_date=None,
        )

        response = self.client.get(
            reverse(self.get_list_url()), data={"saved_search_pk": user_saved_search.pk}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Count the setup too, which make this 17 + 1
        self.assertEqual(response.data["count"], 18)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_owner_type_succeeds(self, *args, **kwargs):

        PropertyFactory()

        self.login_active_user()

        ownership_list = PropertyOwnershipType.active_objects.all().values_list("metadata_entry_id", flat=True)

        type_casted_ownership_list = []

        for ownership_type_id in ownership_list:
            type_casted_ownership_list.append(ownership_type_id)
            PropertyFactory(
                property_info__ownership_type=get_object_or_None(PropertyOwnershipType.active_objects, metadata_entry_id=ownership_type_id)
            )

        response = self.client.get(
            reverse(self.get_list_url()), data={"ownership_type_ids[]": ownership_list}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Count the setup too, which make this 17 + 1
        self.assertEqual(response.data["count"], 18)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_owner_type_with_invalid_format_fails(self, *args, **kwargs):

        self.login_active_user()

        ownership_list = [self.fake.word(), self.fake.word()]

        response = self.client.get(
            reverse(self.get_list_url()), data={"ownership_type_ids[]": ownership_list}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_property_list_with_mls_match_succeeds(self, *args, **kwargs):
        self.login_active_user()
        property_two = PropertyFactory()
        listing_id = property_two.listing_id
        response = self.client.get(
            reverse(self.get_list_url()), data={"search_text": listing_id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["mls_matched"], True)

    def test_get_property_archived_list_with_mls_match_succeeds(self, *args, **kwargs):
        self.login_active_user()
        property_two = PropertyFactory(is_active=False)
        listing_id = property_two.listing_id
        response = self.client.get(
            reverse(self.get_list_url()), data={"search_text": listing_id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["mls_matched"], False)

    def test_get_property_list_with_mls_match_using_saved_search_succeeds(
        self, *args, **kwargs
    ):
        self.login_active_user()
        property_two = PropertyFactory()
        listing_id = property_two.listing_id

        user_saved_search = UserSavedSearchFactory(
            user=self.active_user,
            search_text=listing_id,
            lower_boundary_price_range=None,
            upper_boundary_price_range=None,
            least_amount_of_bedroom=None,
            least_amount_of_bathroom=None,
            ownership_type_ids=None,
            transaction_type_id=None,
            parking_type_ids=None,
            community_search_text="",
            has_video=None,
            from_creation_date=None,
            until_creation_date=None,
            from_listing_contract_date=None,
            until_listing_contract_date=None,
            last_checked_date=None,
        )

        response = self.client.get(
            reverse(self.get_list_url()), data={"saved_search_pk": user_saved_search.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["mls_matched"], True)

    def test_retrieve_property_with_credentials_succeeds(self, *args, **kwargs):
        self.login_active_user()

        property_one = PropertyFactory()
        response = self.client.get(
            reverse(self.get_detail_url(), kwargs={"pk": property_one.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrive_property_without_credentials_fails(self, *args, **kwargs):

        property_one = PropertyFactory()
        response = self.client.get(
            reverse(self.get_detail_url(), kwargs={"pk": property_one.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AutoCompleteTestCases(PropertyCoreBaseTest):
    """
    Authorization test cases auto complete test cases
    """

    base_name = "property"
    extended_name = "address-auto-complete"

    def test_get_auto_complete_list_succeeds(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)), {}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_auto_complete_list_with_uauthenticated_user_succeeds(
        self, *args, **kwargs
    ):
        # Permission deny
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)), {}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_auto_complete_list_with_specific_search_string_succeeds(
        self, *args, **kwargs
    ):
        self.login_active_user()
        # Not a address but this should be able to search check the property list properly
        # This should avoid things like producing an address with faker that's the same with self
        unique_string = str(uuid.uuid4())
        PropertyFactory(address__address_line1=unique_string)
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)),
            data={"search_text": unique_string},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)


class CountResultTestCases(PropertyCoreBaseTest):
    """
    Authorization test cases for count result test cases
    """

    base_name = "property"
    extended_name = "count-results"

    def test_get_count_result_list_succeeds(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)), {}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_count_result_list_with_uauthenticated_user_succeeds(
        self, *args, **kwargs
    ):
        # Permission deny
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)), {}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_count_result_list_with_specific_search_string_succeeds(
        self, *args, **kwargs
    ):
        self.login_active_user()
        # Not a address but this should be able to search check the property list properly
        # This should avoid things like producing an address with faker that's the same with self
        unique_string = str(uuid.uuid4())
        unique_string_2 = str(uuid.uuid4())
        property_two = PropertyFactory(address__city=unique_string)
        list_of_search_texts = [unique_string, unique_string_2]
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)),
            {"search_texts[]": list_of_search_texts},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["search_counts"][property_two.Address.city], 1)
        self.assertEqual(response.data["search_counts"][unique_string_2], 0)


class LuxuriousHouseTestCases(PropertyCoreBaseTest):
    """
    Authorization test cases luxurious houses
    """

    base_name = "property"
    extended_name = "luxurious-houses"
    fake = Faker()
    property_one = None

    def setUp(self, *args, **kwargs):
        self.property_one = PropertyFactory(
            property_info__property_type=PropertyPropertyType.active_objects.get(metadata_entry_id=PropertyPropertyType.SINGLE_FAMILY_METADATA_ENTRY_ID)
        )
        return super().setUp(*args, **kwargs)

    def test_get_property_luxurious_houses_succeeds(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)), {}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_get_property_luxurious_houses_only_get_single_family_succeeds(
        self, *args, **kwargs
    ):
        self.login_active_user()
    
        all_property_type = PropertyPropertyType.active_objects.all()

        for entry in all_property_type:
            PropertyFactory(
                property_info__property_type=entry
            )

        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)), {}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_get_property_luxurious_houses_sorting(self, *args, **kwargs):
        # Test sorting
        self.login_active_user()

        price = self.property_one.Info.price
        lower_price = self.fake.pydecimal(
            right_digits=2, min_value=0, max_value=int(price) - 1
        )
        lower_price_property = PropertyFactory(
            property_info__price=lower_price,
            property_info__property_type=PropertyPropertyType.active_objects.get(metadata_entry_id=PropertyPropertyType.SINGLE_FAMILY_METADATA_ENTRY_ID)
        )
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)), {}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(response.data["results"][0]["id"], self.property_one.pk)
        self.assertEqual(response.data["results"][1]["id"], lower_price_property.pk)

    def test_get_property_luxurious_houses_with_uauthenticated_user_succeeds(
        self, *args, **kwargs
    ):
        # Permission deny
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)), {}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_property_luxurious_houses_with_general_text_specific_search_string_succeeds(
        self, *args, **kwargs
    ):
        self.login_active_user()
        # Not a address but this should be able to search check the property list properly
        # This should avoid things like producing an address with faker that's the same with self
        unique_string = str(uuid.uuid4())
        PropertyFactory(
            full_address=unique_string,
            property_info__property_type=PropertyPropertyType.active_objects.get(metadata_entry_id=PropertyPropertyType.SINGLE_FAMILY_METADATA_ENTRY_ID)
        )
        PropertyFactory(
            unit_number=unique_string,
            property_info__property_type=PropertyPropertyType.active_objects.get(metadata_entry_id=PropertyPropertyType.SINGLE_FAMILY_METADATA_ENTRY_ID)
        )
        PropertyFactory(
            street_number=unique_string,
            property_info__property_type=PropertyPropertyType.active_objects.get(metadata_entry_id=PropertyPropertyType.SINGLE_FAMILY_METADATA_ENTRY_ID)
        )
        PropertyFactory(
            street_name=unique_string,
            property_info__property_type=PropertyPropertyType.active_objects.get(metadata_entry_id=PropertyPropertyType.SINGLE_FAMILY_METADATA_ENTRY_ID)
        )
        PropertyFactory(
            postal_code=unique_string,
            property_info__property_type=PropertyPropertyType.active_objects.get(metadata_entry_id=PropertyPropertyType.SINGLE_FAMILY_METADATA_ENTRY_ID)
        )

        PropertyFactory(
            address__address_line1=unique_string,
            property_info__property_type=PropertyPropertyType.active_objects.get(metadata_entry_id=PropertyPropertyType.SINGLE_FAMILY_METADATA_ENTRY_ID)
        )
        PropertyFactory(
            address__address_line2=unique_string,
            property_info__property_type=PropertyPropertyType.active_objects.get(metadata_entry_id=PropertyPropertyType.SINGLE_FAMILY_METADATA_ENTRY_ID)
        )
        PropertyFactory(
            address__street_number=unique_string,
            property_info__property_type=PropertyPropertyType.active_objects.get(metadata_entry_id=PropertyPropertyType.SINGLE_FAMILY_METADATA_ENTRY_ID)
        )
        PropertyFactory(
            address__street_direction_prefix=unique_string,
            property_info__property_type=PropertyPropertyType.active_objects.get(metadata_entry_id=PropertyPropertyType.SINGLE_FAMILY_METADATA_ENTRY_ID)
        )
        PropertyFactory(
            address__street_name=unique_string,
            property_info__property_type=PropertyPropertyType.active_objects.get(metadata_entry_id=PropertyPropertyType.SINGLE_FAMILY_METADATA_ENTRY_ID)
        )
        PropertyFactory(
            address__street_suffix=unique_string,
            property_info__property_type=PropertyPropertyType.active_objects.get(metadata_entry_id=PropertyPropertyType.SINGLE_FAMILY_METADATA_ENTRY_ID)
        )
        PropertyFactory(
            address__street_direction_suffix=unique_string,
            property_info__property_type=PropertyPropertyType.active_objects.get(metadata_entry_id=PropertyPropertyType.SINGLE_FAMILY_METADATA_ENTRY_ID)
        )
        PropertyFactory(
            address__unit_number=unique_string,
            property_info__property_type=PropertyPropertyType.active_objects.get(metadata_entry_id=PropertyPropertyType.SINGLE_FAMILY_METADATA_ENTRY_ID)
        )
        PropertyFactory(
            address__box_number=unique_string,
            property_info__property_type=PropertyPropertyType.active_objects.get(metadata_entry_id=PropertyPropertyType.SINGLE_FAMILY_METADATA_ENTRY_ID)
        )
        PropertyFactory(
            address__city=unique_string,
            property_info__property_type=PropertyPropertyType.active_objects.get(metadata_entry_id=PropertyPropertyType.SINGLE_FAMILY_METADATA_ENTRY_ID)
        )
        PropertyFactory(
            address__province=unique_string,
            property_info__property_type=PropertyPropertyType.active_objects.get(metadata_entry_id=PropertyPropertyType.SINGLE_FAMILY_METADATA_ENTRY_ID)
        )
        PropertyFactory(
            address__postal_code=unique_string,
            property_info__property_type=PropertyPropertyType.active_objects.get(metadata_entry_id=PropertyPropertyType.SINGLE_FAMILY_METADATA_ENTRY_ID)
        )

        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)),
            data={"search_text": unique_string},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only get the cities
        self.assertEqual(response.data["count"], 1)


class RecentlyAddedTestCases(PropertyCoreBaseTest):
    """
    Authorization test cases for recently added
    """

    base_name = "property"
    extended_name = "recently-added"

    def setUp(self, *args, **kwargs):
        return super().setUp(*args, **kwargs)

    def test_get_property_recently_added_succeeds(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)), {}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_property_recently_added_sorting(self, *args, **kwargs):
        # Test sorting
        self.login_active_user()

        property_one = PropertyFactory()

        creation_date = property_one.Info.listing_contract_date
        past_date = creation_date - timedelta(days=14)
        past_property = PropertyFactory(
            property_info__listing_contract_date=str(past_date)
        )

        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)), {}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["id"], property_one.pk)
        self.assertEqual(response.data["results"][1]["id"], past_property.pk)

    def test_get_property_recently_added_with_uauthenticated_user_succeeds(
        self, *args, **kwargs
    ):
        # Permission deny
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)), {}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_property_recently_added_with_general_text_specific_search_string_succeeds(
        self, *args, **kwargs
    ):
        self.login_active_user()
        # Not a address but this should be able to search check the property list properly
        # This should avoid things like producing an address with faker that's the same with self
        unique_string = str(uuid.uuid4())

        PropertyFactory(full_address=unique_string)
        PropertyFactory(unit_number=unique_string)
        PropertyFactory(street_number=unique_string)
        PropertyFactory(street_name=unique_string)
        PropertyFactory(postal_code=unique_string)

        PropertyFactory(address__address_line1=unique_string)
        PropertyFactory(address__address_line2=unique_string)
        PropertyFactory(address__street_number=unique_string)
        PropertyFactory(address__street_direction_prefix=unique_string)
        PropertyFactory(address__street_name=unique_string)
        PropertyFactory(address__street_suffix=unique_string)
        PropertyFactory(address__street_direction_suffix=unique_string)
        PropertyFactory(address__unit_number=unique_string)
        PropertyFactory(address__box_number=unique_string)
        PropertyFactory(address__city=unique_string)
        PropertyFactory(address__province=unique_string)
        PropertyFactory(address__postal_code=unique_string)

        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)),
            data={"search_text": unique_string},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only get the cities
        self.assertEqual(response.data["count"], 1)


class RecentlyViewedTestCases(PropertyCoreBaseTest):
    """
    Authorization test cases for recently viewed
    """

    base_name = "property"
    extended_name = "recently-viewed"
    property_one = None
    fake = Faker()

    def setUp(self, *args, **kwargs):
        self.property_one = PropertyFactory()
        return super().setUp(*args, **kwargs)

    def test_get_property_recently_viewed_succeeds(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)), {}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_property_recently_viewed_with_uauthenticated_user_fails(
        self, *args, **kwargs
    ):
        # Permission deny
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)), {}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_property_recently_viewed_sorting(self, *args, **kwargs):
        # Test sorting
        self.login_active_user()

        latest_past_date = self.fake.past_datetime(
            tzinfo=timezone.get_current_timezone()
        )
        older_past_date = latest_past_date - timedelta(days=randint(1, 100))

        latest_history = UserPropertyHistoryFactory(
            content_object=PropertyFactory(),
            user=self.active_user,
            history_type=UserHistory.VIEWED,
        )

        latest_history.date_created = latest_past_date
        latest_history.save()

        older_history = UserPropertyHistoryFactory(
            content_object=PropertyFactory(),
            user=self.active_user,
            history_type=UserHistory.VIEWED,
        )
        older_history.date_created = older_past_date
        older_history.save()

        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)), {}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["id"], latest_history.object_id)
        self.assertEqual(response.data["results"][1]["id"], older_history.object_id)

    def test_get_property_recently_viewed_with_general_text_specific_search_string_succeeds(
        self, *args, **kwargs
    ):
        self.login_active_user()
        # Not a address but this should be able to search check the property list properly
        # This should avoid things like producing an address with faker that's the same with self
        unique_string = str(uuid.uuid4())

        UserPropertyHistoryFactory(
            content_object=PropertyFactory(full_address=unique_string),
            user=self.active_user,
            history_type=UserHistory.VIEWED,
        )

        UserPropertyHistoryFactory(
            content_object=PropertyFactory(unit_number=unique_string),
            user=self.active_user,
            history_type=UserHistory.VIEWED,
        )
        UserPropertyHistoryFactory(
            content_object=PropertyFactory(street_number=unique_string),
            user=self.active_user,
            history_type=UserHistory.VIEWED,
        )
        UserPropertyHistoryFactory(
            content_object=PropertyFactory(street_name=unique_string),
            user=self.active_user,
            history_type=UserHistory.VIEWED,
        )
        UserPropertyHistoryFactory(
            content_object=PropertyFactory(postal_code=unique_string),
            user=self.active_user,
            history_type=UserHistory.VIEWED,
        )
        UserPropertyHistoryFactory(
            content_object=PropertyFactory(address__address_line1=unique_string),
            user=self.active_user,
            history_type=UserHistory.VIEWED,
        )
        UserPropertyHistoryFactory(
            content_object=PropertyFactory(address__address_line2=unique_string),
            user=self.active_user,
            history_type=UserHistory.VIEWED,
        )
        UserPropertyHistoryFactory(
            content_object=PropertyFactory(address__street_number=unique_string),
            user=self.active_user,
            history_type=UserHistory.VIEWED,
        )
        UserPropertyHistoryFactory(
            content_object=PropertyFactory(
                address__street_direction_prefix=unique_string
            ),
            user=self.active_user,
            history_type=UserHistory.VIEWED,
        )
        UserPropertyHistoryFactory(
            content_object=PropertyFactory(address__street_name=unique_string),
            user=self.active_user,
            history_type=UserHistory.VIEWED,
        )
        UserPropertyHistoryFactory(
            content_object=PropertyFactory(address__street_suffix=unique_string),
            user=self.active_user,
            history_type=UserHistory.VIEWED,
        )
        UserPropertyHistoryFactory(
            content_object=PropertyFactory(
                address__street_direction_suffix=unique_string
            ),
            user=self.active_user,
            history_type=UserHistory.VIEWED,
        )
        UserPropertyHistoryFactory(
            content_object=PropertyFactory(address__unit_number=unique_string),
            user=self.active_user,
            history_type=UserHistory.VIEWED,
        )
        UserPropertyHistoryFactory(
            content_object=PropertyFactory(address__box_number=unique_string),
            user=self.active_user,
            history_type=UserHistory.VIEWED,
        )
        UserPropertyHistoryFactory(
            content_object=PropertyFactory(address__city=unique_string),
            user=self.active_user,
            history_type=UserHistory.VIEWED,
        )
        UserPropertyHistoryFactory(
            content_object=PropertyFactory(address__province=unique_string),
            user=self.active_user,
            history_type=UserHistory.VIEWED,
        )
        UserPropertyHistoryFactory(
            content_object=PropertyFactory(address__postal_code=unique_string),
            user=self.active_user,
            history_type=UserHistory.VIEWED,
        )

        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)),
            data={"search_text": unique_string},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only check the city
        self.assertEqual(response.data["count"], 1)


class NearbyHomesTestCases(PropertyCoreBaseTest):
    """
    Authorization test cases nearby houses
    """

    base_name = "property"
    extended_name = "nearby-homes"
    fake = Faker()
    property_one = None

    def setUp(self, *args, **kwargs):
        self.property_one = PropertyFactory()
        return super().setUp(*args, **kwargs)

    def test_get_property_nearby_homes_succeeds(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)),
            {"lng": self.fake.longitude(), "lat": self.fake.latitude()},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_property_nearby_homes_with_uauthenticated_user_succeeds(
        self, *args, **kwargs
    ):
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)),
            {"lng": self.fake.longitude(), "lat": self.fake.latitude()},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_property_nearby_homes_with_uauthenticated_user_fails(
        self, *args, **kwargs
    ):
        # Bad request!
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name))
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_property_nearby_homes_without_longtitude_fails(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)),
            {"lng": self.fake.longitude()},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_property_nearby_homes_without_latitude_fails(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)),
            {"lat": self.fake.latitude()},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_property_nearby_homes_with_general_text_specific_search_string_succeeds(
        self, *args, **kwargs
    ):
        self.login_active_user()
        # Not a address but this should be able to search check the property list properly
        # This should avoid things like producing an address with faker that's the same with self
        unique_string = str(uuid.uuid4())

        lng = float(self.fake.longitude())
        lat = float(self.fake.latitude())

        PropertyFactory(
            full_address=unique_string, geo_location__coordinates=Point(lng, lat)
        )
        PropertyFactory(
            unit_number=unique_string, geo_location__coordinates=Point(lng, lat)
        )
        PropertyFactory(
            street_number=unique_string, geo_location__coordinates=Point(lng, lat)
        )
        PropertyFactory(
            street_name=unique_string, geo_location__coordinates=Point(lng, lat)
        )
        PropertyFactory(
            postal_code=unique_string, geo_location__coordinates=Point(lng, lat)
        )

        PropertyFactory(
            address__address_line1=unique_string,
            geo_location__coordinates=Point(lng, lat),
        )
        PropertyFactory(
            address__address_line2=unique_string,
            geo_location__coordinates=Point(lng, lat),
        )
        PropertyFactory(
            address__street_number=unique_string,
            geo_location__coordinates=Point(lng, lat),
        )
        PropertyFactory(
            address__street_direction_prefix=unique_string,
            geo_location__coordinates=Point(lng, lat),
        )
        PropertyFactory(
            address__street_name=unique_string, geo_location__coordinates=Point(lng, lat)
        )
        PropertyFactory(
            address__street_suffix=unique_string,
            geo_location__coordinates=Point(lng, lat),
        )
        PropertyFactory(
            address__street_direction_suffix=unique_string,
            geo_location__coordinates=Point(lng, lat),
        )
        PropertyFactory(
            address__unit_number=unique_string, geo_location__coordinates=Point(lng, lat)
        )
        PropertyFactory(
            address__box_number=unique_string, geo_location__coordinates=Point(lng, lat)
        )
        PropertyFactory(
            address__city=unique_string, geo_location__coordinates=Point(lng, lat)
        )
        PropertyFactory(
            address__province=unique_string, geo_location__coordinates=Point(lng, lat)
        )
        PropertyFactory(
            address__postal_code=unique_string, geo_location__coordinates=Point(lng, lat)
        )

        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)),
            data={"search_text": unique_string, "lng": lng, "lat": lat},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 17)
