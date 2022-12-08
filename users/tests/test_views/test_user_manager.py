import uuid
from random import randint

from core.shortcuts import get_object_or_None
from crea_parser.tests.factories.property import PropertyFactory
from django.urls import reverse
from faker import Faker
from homeswipr.tests.factories.property_favorite import PropertyFavoriteFactory
from rest_framework import status
from users.models import HomeswiprEmailAddress, UserHistory
from users.tests.factories.referral import ReferralFactory
from users.tests.factories.user import UserFactory
from users.tests.factories.user_history import UserPropertyHistoryFactory

from .base_app_test import UserTestCases


class UserManagerTestCases(UserTestCases):
    """
    User Manager test cases
    """

    fake = Faker()
    valid_data = {}

    base_name = "users_manager"

    def setUp(self, *args, **kwargs):

        self.valid_data = {"email": f"{self.fake.email()}"}

        self.invalid_data = {"email": f"{self.fake.first_name()}"}

        # Archived user, should not be gotten
        UserFactory(is_active=False)

        return super().setUp(*args, **kwargs)

    def test_list_user_manager_succeeds(self, *args, **kwargs):
        self.login_users_manager_user()
        response = self.client.get(reverse(self.get_list_url()), {})
        self.assertEqual(response.data["count"], 5)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_user_manager_with_normal_user_fails(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.get(reverse(self.get_list_url()), {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_user_manager_with_search_succeeds(self, *args, **kwargs):

        self.login_users_manager_user()

        # Not a valid fake but this should properly test the user manager search
        name = self.fake.name()
        email = f"{name}{str(randint(1, 100))}@{self.fake.free_email_domain()}".lower()
        UserFactory(first_name=name)
        UserFactory(last_name=name)
        UserFactory(email=email)

        response = self.client.get(
            reverse(self.get_list_url()), data={"user_search_text": name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

    def test_list_user_manager_with_super_user_succeeds(self, *args, **kwargs):
        self.login_super_user()
        response = self.client.get(reverse(self.get_list_url()), {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_user_manager_without_auth_fails(self, *args, **kwargs):
        response = self.client.get(reverse(self.get_list_url()), {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_user_manager_succeeds(self, *args, **kwargs):
        self.login_users_manager_user()
        response = self.client.get(
            reverse(self.get_detail_url(), kwargs={"pk": self.active_user.pk}), {}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_user_manager_with_normal_user_fails(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.get(
            reverse(self.get_detail_url(), kwargs={"pk": self.active_user.pk}), {}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_user_manager_with_super_user_succeeds(self, *args, **kwargs):
        self.login_super_user()
        response = self.client.get(
            reverse(self.get_detail_url(), kwargs={"pk": self.active_user.pk}), {}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_user_manager_without_auth_fails(self, *args, **kwargs):
        response = self.client.get(
            reverse(self.get_detail_url(), kwargs={"pk": self.active_user.pk}), {}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_super_user_succeeds(self, *args, **kwargs):
        self.login_users_manager_user()
        response = self.client.patch(
            reverse(self.get_detail_url(), kwargs={"pk": self.active_user.pk}),
            self.valid_data,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        email = get_object_or_None(
            HomeswiprEmailAddress,
            user=self.active_user,
            email=self.valid_data.get("email", ""),
        )
        self.assertIsNotNone(email)

    def test_patch_user_manager_with_normal_user_fails(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.patch(
            reverse(self.get_detail_url(), kwargs={"pk": self.active_user.pk}),
            self.valid_data,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_user_manager_with_super_user_succeeds(self, *args, **kwargs):
        self.login_super_user()
        response = self.client.patch(
            reverse(self.get_detail_url(), kwargs={"pk": self.active_user.pk}),
            data=self.valid_data,
        )

        email = get_object_or_None(
            HomeswiprEmailAddress,
            user=self.active_user,
            email=self.valid_data.get("email", ""),
        )
        self.assertIsNotNone(email)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_user_manager_without_auth_fails(self, *args, **kwargs):
        response = self.client.patch(
            reverse(self.get_detail_url(), kwargs={"pk": self.active_user.pk}),
            self.valid_data,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_valid_but_invalid_data_fails(self, *args, **kwargs):
        self.login_users_manager_user()
        response = self.client.patch(
            reverse(self.get_detail_url(), kwargs={"pk": self.active_user.pk}),
            self.invalid_data,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserManagerListOfFavoriteTestCases(UserTestCases):

    fake = Faker()
    base_name = "users_manager"
    extended_name = "user-list-of-favorites"

    def setUp(self, *args, **kwargs):

        return_value = super().setUp(*args, **kwargs)
        PropertyFavoriteFactory(user=self.active_user)
        PropertyFavoriteFactory(user=self.active_user, is_active=False)
        PropertyFavoriteFactory(
            user=self.active_user, favorited_property__is_active=False
        )
        return return_value

    def test_user_manager_listing_of_all_favorites_succeeds(self, *args, **kwargs):
        self.login_users_manager_user()
        response = self.client.get(
            reverse(
                self.get_custom_action_url(self.extended_name),
                kwargs={"pk": self.active_user.pk},
            ),
            {},
        )
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_manager_listing_of_all_favorites_with_normal_user_fails(
        self, *args, **kwargs
    ):
        self.login_active_user()
        response = self.client.get(
            reverse(
                self.get_custom_action_url(self.extended_name),
                kwargs={"pk": self.active_user.pk},
            ),
            {},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_manager_listing_of_all_favorites_unauth_fails(self, *args, **kwargs):
        response = self.client.get(
            reverse(
                self.get_custom_action_url(self.extended_name),
                kwargs={"pk": self.active_user.pk},
            ),
            {},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_manager_listing_of_all_favorites_with_super_user_succeeds(
        self, *args, **kwargs
    ):
        self.login_super_user()
        response = self.client.get(
            reverse(
                self.get_custom_action_url(self.extended_name),
                kwargs={"pk": self.active_user.pk},
            ),
            {},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_manager_listing_of_all_favorites_with_search_text(
        self, *args, **kwargs
    ):
        self.login_users_manager_user()

        # Not a address but this should be able to search check the property list properly
        # This should avoid things like producing an address with faker that's the same with self

        unique_string = str(uuid.uuid4())

        PropertyFavoriteFactory(
            user=self.active_user,
            favorited_property=PropertyFactory(full_address=unique_string),
        )
        PropertyFavoriteFactory(
            user=self.active_user,
            favorited_property=PropertyFactory(unit_number=unique_string),
        )
        PropertyFavoriteFactory(
            user=self.active_user,
            favorited_property=PropertyFactory(street_number=unique_string),
        )
        PropertyFavoriteFactory(
            user=self.active_user,
            favorited_property=PropertyFactory(street_name=unique_string),
        )
        PropertyFavoriteFactory(
            user=self.active_user,
            favorited_property=PropertyFactory(postal_code=unique_string),
        )

        PropertyFavoriteFactory(
            user=self.active_user,
            favorited_property=PropertyFactory(address__address_line1=unique_string),
        )
        PropertyFavoriteFactory(
            user=self.active_user,
            favorited_property=PropertyFactory(address__address_line2=unique_string),
        )
        PropertyFavoriteFactory(
            user=self.active_user,
            favorited_property=PropertyFactory(address__street_number=unique_string),
        )
        PropertyFavoriteFactory(
            user=self.active_user,
            favorited_property=PropertyFactory(
                address__street_direction_prefix=unique_string
            ),
        )
        PropertyFavoriteFactory(
            user=self.active_user,
            favorited_property=PropertyFactory(address__street_name=unique_string),
        )
        PropertyFavoriteFactory(
            user=self.active_user,
            favorited_property=PropertyFactory(address__street_suffix=unique_string),
        )
        PropertyFavoriteFactory(
            user=self.active_user,
            favorited_property=PropertyFactory(
                address__street_direction_suffix=unique_string
            ),
        )
        PropertyFavoriteFactory(
            user=self.active_user,
            favorited_property=PropertyFactory(address__unit_number=unique_string),
        )
        PropertyFavoriteFactory(
            user=self.active_user,
            favorited_property=PropertyFactory(address__box_number=unique_string),
        )
        PropertyFavoriteFactory(
            user=self.active_user,
            favorited_property=PropertyFactory(address__city=unique_string),
        )
        PropertyFavoriteFactory(
            user=self.active_user,
            favorited_property=PropertyFactory(address__province=unique_string),
        )
        PropertyFavoriteFactory(
            user=self.active_user,
            favorited_property=PropertyFactory(address__postal_code=unique_string),
        )

        response = self.client.get(
            reverse(
                self.get_custom_action_url(self.extended_name),
                kwargs={"pk": self.active_user.pk},
            ),
            {"search_text": unique_string},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 17)


class UserManagerListOfRecentlyViewedTestCases(UserTestCases):

    fake = Faker()
    base_name = "users_manager"
    extended_name = "user-recently-viewed"

    def setUp(self, *args, **kwargs):

        return_value = super().setUp(*args, **kwargs)
        PropertyFavoriteFactory(user=self.active_user)
        return return_value

    def test_user_manager_listing_of_user_recently_viewed_succeeds(
        self, *args, **kwargs
    ):
        self.login_users_manager_user()
        response = self.client.get(
            reverse(
                self.get_custom_action_url(self.extended_name),
                kwargs={"pk": self.active_user.pk},
            ),
            {},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_manager_listing_of_user_recently_viewed_with_normal_user_fails(
        self, *args, **kwargs
    ):
        self.login_active_user()
        response = self.client.get(
            reverse(
                self.get_custom_action_url(self.extended_name),
                kwargs={"pk": self.active_user.pk},
            ),
            {},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_manager_listing_of_user_recently_viewed_unauth_fails(
        self, *args, **kwargs
    ):
        response = self.client.get(
            reverse(
                self.get_custom_action_url(self.extended_name),
                kwargs={"pk": self.active_user.pk},
            ),
            {},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_manager_listing_of_user_recently_viewed_with_super_user_succeeds(
        self, *args, **kwargs
    ):
        self.login_super_user()
        response = self.client.get(
            reverse(
                self.get_custom_action_url(self.extended_name),
                kwargs={"pk": self.active_user.pk},
            ),
            {},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_manager_listing_of_user_recently_viewed_with_search_text(
        self, *args, **kwargs
    ):
        self.login_users_manager_user()
        # Not a address but this should be able to search check the property list properly
        # This should avoid things like producing an address with faker that's the same with self
        # self.property_one
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
            reverse(
                self.get_custom_action_url(self.extended_name),
                kwargs={"pk": self.active_user.pk},
            ),
            {"search_text": unique_string},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 17)


class UserManagerReferralTestCases(UserTestCases):

    fake = Faker()
    base_name = "users_manager"
    extended_name = "referrals"

    def setUp(self, *args, **kwargs):

        return_value = super().setUp(*args, **kwargs)
        return return_value

    def test_user_manager_referral_by_user_succeeds(self, *args, **kwargs):
        self.login_users_manager_user()

        ReferralFactory(referred_by=self.active_user)

        response = self.client.get(
            reverse(
                self.get_custom_action_url(self.extended_name),
                kwargs={"pk": self.active_user.pk},
            ),
            {},
        )
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_manager_referral_by_user_with_normal_user_fails(
        self, *args, **kwargs
    ):
        self.login_active_user()
        ReferralFactory(referred_by=self.active_user)

        response = self.client.get(
            reverse(
                self.get_custom_action_url(self.extended_name),
                kwargs={"pk": self.active_user.pk},
            ),
            {},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_manager_referral_by_user_unauth_fails(self, *args, **kwargs):
        ReferralFactory(referred_by=self.active_user)

        response = self.client.get(
            reverse(
                self.get_custom_action_url(self.extended_name),
                kwargs={"pk": self.active_user.pk},
            ),
            {},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_manager_referral_by_user_with_super_user_succeeds(
        self, *args, **kwargs
    ):
        self.login_super_user()
        response = self.client.get(
            reverse(
                self.get_custom_action_url(self.extended_name),
                kwargs={"pk": self.active_user.pk},
            ),
            {},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
