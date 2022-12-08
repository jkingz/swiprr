import decimal
import uuid
from random import randint

from crea_parser.tests.utils import (
    produce_list_of_owner_ship_type_ids,
    produce_list_of_parking_type_ids,
)
from dateutil import parser
from ddf_manager.ddf_logger import logger
from django.urls import reverse
from django.utils import timezone
from faker import Faker
from homeswipr.tests.factories.user_saved_search import UserSavedSearchFactory
from rest_framework import status

from .base_app_test import CoreBaseTest


class SavedSearchCoreTestCases(CoreBaseTest):

    fake = Faker()

    def setUp(self, *args, **kwargs):

        self.saved_search_valid_data = {
            "title": self.fake.word(),
            "search_text": self.fake.word(),
            "lower_boundary_price_range": self.fake.pydecimal(
                right_digits=2, max_value=100000000000
            ),
            "upper_boundary_price_range": self.fake.pydecimal(
                right_digits=2, max_value=100000000000
            ),
            "least_amount_of_bedroom": randint(0, 10),
            "least_amount_of_bathroom": randint(0, 10),
            "ownership_type_ids": produce_list_of_owner_ship_type_ids(),
            "transaction_type_id": randint(1, 4),
            "parking_type_ids": produce_list_of_parking_type_ids(),
            "community_search_text": self.fake.word(),
            "has_video": self.fake.pybool(),
            "from_creation_date": self.fake.past_datetime(
                tzinfo=timezone.get_current_timezone()
            ),
            "until_creation_date": self.fake.past_datetime(
                tzinfo=timezone.get_current_timezone()
            ),
            "from_listing_contract_date": self.fake.past_datetime(
                tzinfo=timezone.get_current_timezone()
            ),
            "until_listing_contract_date": self.fake.past_datetime(
                tzinfo=timezone.get_current_timezone()
            ),
        }

        self.saved_search_invalid_data = {"title": None}

        return super().setUp(args, kwargs)

    def assert_common_return_data(self, to_validate_data):
        self.assertEqual(
            to_validate_data.get("title", None),
            self.saved_search_valid_data.get("title", None),
        )
        self.assertEqual(
            to_validate_data.get("search_text", None),
            self.saved_search_valid_data.get("search_text", None),
        )
        self.assertEqual(
            decimal.Decimal(to_validate_data.get("lower_boundary_price_range", 0)),
            self.saved_search_valid_data.get("lower_boundary_price_range", 0),
        )
        self.assertEqual(
            decimal.Decimal(to_validate_data.get("upper_boundary_price_range", 0)),
            self.saved_search_valid_data.get("upper_boundary_price_range", 0),
        )
        self.assertEqual(
            to_validate_data.get("least_amount_of_bedroom", None),
            self.saved_search_valid_data.get("least_amount_of_bedroom", None),
        )
        self.assertEqual(
            to_validate_data.get("least_amount_of_bathroom", None),
            self.saved_search_valid_data.get("least_amount_of_bathroom", None),
        )
        self.assertEqual(
            to_validate_data.get("ownership_type_ids", []),
            self.saved_search_valid_data.get("ownership_type_ids", []),
        )
        self.assertEqual(
            to_validate_data.get("transaction_type_id", None),
            self.saved_search_valid_data.get("transaction_type_id", None),
        )
        self.assertEqual(
            to_validate_data.get("parking_type_ids", []),
            self.saved_search_valid_data.get("parking_type_ids", []),
        )
        self.assertEqual(
            to_validate_data.get("community_search_text", None),
            self.saved_search_valid_data.get("community_search_text", None),
        )
        self.assertEqual(
            to_validate_data.get("has_video", None),
            self.saved_search_valid_data.get("has_video", None),
        )
        self.assertEqual(
            parser.parse(to_validate_data.get("from_creation_date", None)),
            self.saved_search_valid_data.get("from_creation_date", None),
        )
        self.assertEqual(
            parser.parse(to_validate_data.get("until_creation_date", None)),
            self.saved_search_valid_data.get("until_creation_date", None),
        )
        self.assertEqual(
            parser.parse(to_validate_data.get("from_listing_contract_date", None)),
            self.saved_search_valid_data.get("from_listing_contract_date", None),
        )
        self.assertEqual(
            parser.parse(to_validate_data.get("until_listing_contract_date", None)),
            self.saved_search_valid_data.get("until_listing_contract_date", None),
        )


class SavedSearchTestCases(SavedSearchCoreTestCases):
    """
    Authorization test cases for favorit agent
    """

    base_name = "saved-search"

    def setUp(self, *args, **kwargs):

        value = super().setUp(*args, **kwargs)

        UserSavedSearchFactory(user=self.active_user, is_active=False)

        return value

    def test_get_list_saved_search_succeeds(self, *args, **kwargs):
        self.login_active_user()

        # Not an exact fit for the property but this should be able to search
        # check the search functionality of the saved search list properly
        unique_string = str(uuid.uuid4())

        UserSavedSearchFactory(title=unique_string, user=self.active_user)
        UserSavedSearchFactory(search_text=unique_string, user=self.active_user)
        UserSavedSearchFactory(
            community_search_text=unique_string, user=self.active_user
        )

        # Checks if it can list other user
        UserSavedSearchFactory(
            community_search_text=unique_string, user=self.other_user
        )

        response = self.client.get(
            reverse(self.get_list_url()), data={"search_text": unique_string}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

    def test_get_list_saved_search_with_unauth_user_fails(self, *args, **kwargs):

        response = self.client.get(reverse(self.get_list_url()))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_retrieve_saved_search_succeeds(self, *args, **kwargs):
        self.login_active_user()
        user_saved_search = UserSavedSearchFactory(user=self.active_user)
        response = self.client.get(
            reverse(self.get_detail_url(), kwargs={"pk": user_saved_search.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_retrieve_saved_search_with_user_manager_succeeds(
        self, *args, **kwargs
    ):
        self.login_users_manager_user()
        user_saved_search = UserSavedSearchFactory(user=self.active_user)
        response = self.client.get(
            reverse(self.get_detail_url(), kwargs={"pk": user_saved_search.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_retrieve_saved_search_with_super_user_succeeds(self, *args, **kwargs):
        self.login_super_user()
        user_saved_search = UserSavedSearchFactory(user=self.active_user)
        response = self.client.get(
            reverse(self.get_detail_url(), kwargs={"pk": user_saved_search.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_retrieve_archived_saved_search_succeeds(self, *args, **kwargs):
        self.login_active_user()
        user_saved_search = UserSavedSearchFactory(
            user=self.active_user, is_active=False
        )
        response = self.client.get(
            reverse(self.get_detail_url(), kwargs={"pk": user_saved_search.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_retrieve_saved_search_with_unauth_user_fails(self, *args, **kwargs):
        user_saved_search = UserSavedSearchFactory(user=self.active_user)
        response = self.client.get(
            reverse(self.get_detail_url(), kwargs={"pk": user_saved_search.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_retrieve_saved_search_with_other_user_fails(self, *args, **kwargs):
        self.login_other_user()
        user_saved_search = UserSavedSearchFactory(user=self.active_user)

        response = self.client.get(
            reverse(self.get_detail_url(), kwargs={"pk": user_saved_search.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_create_saved_search_succeeds(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.post(
            reverse(self.get_list_url()), self.saved_search_valid_data
        )
        self.assert_common_return_data(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_create_saved_search_with_passed_other_user_ignored_but_succeeds(
        self, *args, **kwargs
    ):

        self.login_active_user()

        injected_user_but_valid_data = self.saved_search_valid_data

        injected_user_but_valid_data["user"] = self.other_user.pk
        response = self.client.post(
            reverse(self.get_list_url()), injected_user_but_valid_data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.active_user.pk, response.data["user"])
        self.assert_common_return_data(response.data)

    def test_post_create_saved_search_with_passed_created_by_ignored_but_succeeds(
        self, *args, **kwargs
    ):

        self.login_active_user()

        user_saved_search = UserSavedSearchFactory(user=self.active_user)
        injected_user_but_valid_data = self.saved_search_valid_data

        injected_user_but_valid_data["created_by"] = self.other_user.pk

        response = self.client.post(
            reverse(self.get_list_url()), injected_user_but_valid_data
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assert_common_return_data(response.data)
        self.assertEqual(self.active_user.pk, response.data["created_by"])

    def test_post_create_saved_search_with_unauth_fails(self, *args, **kwargs):

        response = self.client.post(
            reverse(self.get_list_url()), self.saved_search_valid_data
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_create_saved_search_with_empty_data_fails(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.post(reverse(self.get_list_url()), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_update_saved_search_succeeds(self, *args, **kwargs):
        self.login_active_user()

        user_saved_search = UserSavedSearchFactory(user=self.active_user)
        response = self.client.patch(
            reverse(self.get_detail_url(), kwargs={"pk": user_saved_search.pk}),
            self.saved_search_valid_data,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_common_return_data(response.data)

    def test_patch_update_saved_search_with_passed_created_by_ignored_but_succeeds(
        self, *args, **kwargs
    ):
        self.login_active_user()

        user_saved_search = UserSavedSearchFactory(
            user=self.active_user, created_by=self.active_user
        )
        injected_user_data = self.saved_search_valid_data

        injected_user_data["created_by"] = self.other_user.pk

        response = self.client.patch(
            reverse(self.get_detail_url(), kwargs={"pk": user_saved_search.pk}),
            injected_user_data,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_common_return_data(response.data)
        self.assertEqual(self.active_user.pk, response.data["created_by"])

    def test_patch_update_saved_search_with_passed_user_but_still_save_the_logged_in_succeeds(
        self, *args, **kwargs
    ):
        self.login_active_user()

        user_saved_search = UserSavedSearchFactory(user=self.active_user)
        injected_user_data = self.saved_search_valid_data

        injected_user_data["user"] = self.other_user.pk

        response = self.client.patch(
            reverse(self.get_detail_url(), kwargs={"pk": user_saved_search.pk}),
            injected_user_data,
        )
        self.assert_common_return_data(response.data)

        self.assertEqual(self.active_user.pk, response.data["user"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_update_saved_search_with_user_manager_and_passed_created_by_ignored_but_succeeds(
        self, *args, **kwargs
    ):
        self.login_users_manager_user()

        user_saved_search = UserSavedSearchFactory(
            user=self.active_user, created_by=self.users_manager_user
        )
        injected_user_data = self.saved_search_valid_data

        injected_user_data["created_by"] = self.other_user.pk

        response = self.client.patch(
            reverse(self.get_detail_url(), kwargs={"pk": user_saved_search.pk}),
            injected_user_data,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_common_return_data(response.data)
        self.assertEqual(self.users_manager_user.pk, response.data["created_by"])

    def test_patch_update_saved_search_with_superuser_and_passed_created_by_ignored_but_succeeds(
        self, *args, **kwargs
    ):
        self.login_super_user()

        user_saved_search = UserSavedSearchFactory(
            user=self.active_user, created_by=self.super_user
        )
        injected_user_data = self.saved_search_valid_data

        injected_user_data["created_by"] = self.other_user.pk

        response = self.client.patch(
            reverse(self.get_detail_url(), kwargs={"pk": user_saved_search.pk}),
            injected_user_data,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_common_return_data(response.data)
        self.assertEqual(self.super_user.pk, response.data["created_by"])

    def test_patch_update_saved_search_with_user_manager_passed_user_succeeds(
        self, *args, **kwargs
    ):
        self.login_users_manager_user()

        user_saved_search = UserSavedSearchFactory(user=self.active_user)
        injected_user_data = self.saved_search_valid_data

        injected_user_data["user"] = self.other_user.pk

        response = self.client.patch(
            reverse(self.get_detail_url(), kwargs={"pk": user_saved_search.pk}),
            injected_user_data,
        )
        self.assert_common_return_data(response.data)

        self.assertEqual(self.other_user.pk, response.data["user"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_update_saved_search_with_super_user_passed_user_succeeds(
        self, *args, **kwargs
    ):
        self.login_super_user()

        user_saved_search = UserSavedSearchFactory(user=self.active_user)
        injected_user_data = self.saved_search_valid_data

        injected_user_data["user"] = self.other_user.pk

        response = self.client.patch(
            reverse(self.get_detail_url(), kwargs={"pk": user_saved_search.pk}),
            injected_user_data,
        )
        self.assert_common_return_data(response.data)

        self.assertEqual(self.other_user.pk, response.data["user"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_update_saved_search_with_unauth_fails(self, *args, **kwargs):

        user_saved_search = UserSavedSearchFactory(user=self.active_user)
        response = self.client.patch(
            reverse(self.get_detail_url(), kwargs={"pk": user_saved_search.pk}),
            self.saved_search_valid_data,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_update_saved_search_with_another_user_fails(self, *args, **kwargs):
        self.login_other_user()

        user_saved_search = UserSavedSearchFactory(user=self.active_user)
        response = self.client.patch(
            reverse(self.get_detail_url(), kwargs={"pk": user_saved_search.pk}),
            self.saved_search_valid_data,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_update_saved_search_with_empty_succeeds(self, *args, **kwargs):
        # Patch, even with empty data still succeeds

        self.login_active_user()

        user_saved_search = UserSavedSearchFactory(user=self.active_user)
        response = self.client.patch(
            reverse(self.get_detail_url(), kwargs={"pk": user_saved_search.pk}), {}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_saved_search_succeeds(self, *args, **kwargs):

        self.login_active_user()

        user_saved_search = UserSavedSearchFactory(user=self.active_user)

        response = self.client.delete(
            reverse(self.get_detail_url(), kwargs={"pk": user_saved_search.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_saved_search_with_unauth_fails(self, *args, **kwargs):

        user_saved_search = UserSavedSearchFactory(user=self.active_user)

        response = self.client.delete(
            reverse(self.get_detail_url(), kwargs={"pk": user_saved_search.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_saved_search_with_other_user_fails(self, *args, **kwargs):

        self.login_other_user()

        user_saved_search = UserSavedSearchFactory(user=self.active_user)

        response = self.client.delete(
            reverse(self.get_detail_url(), kwargs={"pk": user_saved_search.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
