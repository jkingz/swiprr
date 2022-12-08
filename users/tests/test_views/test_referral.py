from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from faker import Faker
from rest_framework import status
from users.tests.factories.referral import ReferralFactory
from users.tests.factories.user import UserFactory

from .base_app_test import UserTestCases


class ReferralTestCases(UserTestCases):

    fake = Faker()

    base_name = "referral"

    def test_get_all_my_referrals_with_auth_succeeds(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.get(reverse(self.get_list_url()))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_my_referrals_with_unauth_fails(self, *args, **kwargs):
        response = self.client.get(reverse(self.get_list_url()))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_all_my_referrals_with_search_text_succeeds(self, *args, **kwargs):
        self.login_active_user()

        # Not a person but this should be able to search check if our list works
        # properly
        unique_string = "this_is_a_unique_string"
        unique_mail = f"{unique_string}@example.com"

        user_with_unique_first_name = UserFactory(first_name=unique_string)
        user_with_unique_last_name = UserFactory(last_name=unique_string)
        user_with_unique_email = UserFactory(email=unique_mail)

        ReferralFactory(
            referred_by=self.active_user, invited_user=user_with_unique_email
        )
        ReferralFactory(
            referred_by=self.active_user, invited_user=user_with_unique_first_name
        )
        ReferralFactory(
            referred_by=self.active_user, invited_user=user_with_unique_last_name
        )
        ReferralFactory()

        response = self.client.get(
            reverse(self.get_list_url()), {"search_text": unique_string}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

    def test_retrieve_a_referral_with_auth_and_owner_succeeds(self, *args, **kwargs):
        self.login_active_user()

        referral = ReferralFactory(referred_by=self.active_user)
        response = self.client.get(
            reverse(self.get_detail_url(), kwargs={"pk": referral.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_a_referral_with_auth_and_not_owner_fails(self, *args, **kwargs):
        self.login_active_user()

        referral = ReferralFactory(referred_by=self.other_user)
        response = self.client.get(
            reverse(self.get_detail_url(), kwargs={"pk": referral.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_a_referral_with_auth_and_super_user_succeeds(
        self, *args, **kwargs
    ):
        self.login_super_user()

        referral = ReferralFactory(referred_by=self.active_user)
        response = self.client.get(
            reverse(self.get_detail_url(), kwargs={"pk": referral.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_a_referral_with_auth_and_user_manager_succeeds(
        self, *args, **kwargs
    ):
        self.login_users_manager_user()

        referral = ReferralFactory(referred_by=self.active_user)
        response = self.client.get(
            reverse(self.get_detail_url(), kwargs={"pk": referral.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_a_referral_with_unauth_user_fails(self, *args, **kwargs):
        referral = ReferralFactory(referred_by=self.active_user)
        response = self.client.get(
            reverse(self.get_detail_url(), kwargs={"pk": referral.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ConvertReferralTokenToFirstNameTestCases(UserTestCases):
    """
    Authorization test cases for referral test case
    """

    fake = Faker()

    base_name = "referral"
    extended_name = "convert-token-to-first-name"

    def test_get_referral_with_auth_succeeds(self, *args, **kwargs):
        self.login_active_user()
        self.active_user.referral_code_expiry_date = timezone.now() + timedelta(days=7)
        self.active_user.save()
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)),
            {"referral_code": self.active_user.referral_code},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_referral_without_auth_succeeds(self, *args, **kwargs):
        self.active_user.referral_code_expiry_date = timezone.now() + timedelta(days=7)
        self.active_user.save()
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)),
            {"referral_code": self.active_user.referral_code},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_referral_with_expired_token_and_unauth_fails(self, *args, **kwargs):
        self.active_user.referral_code_expiry_date = timezone.now() - timedelta(days=7)
        self.active_user.save()
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)),
            {"referral_code": self.active_user.referral_code},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_referral_with_expired_token_and_auth_fails(self, *args, **kwargs):
        self.login_active_user()
        self.active_user.referral_code_expiry_date = timezone.now() - timedelta(days=7)
        self.active_user.save()
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)),
            {"referral_code": self.active_user.referral_code},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_referral_with_does_not_exists_and_unauth_token_fails(
        self, *args, **kwargs
    ):
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)),
            {"referral_code": "not_valid_token"},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_referral_with_does_not_exists_and_auth_token_fails(
        self, *args, **kwargs
    ):
        self.login_active_user()
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name)),
            {"referral_code": "not_valid_token"},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_referral_without_params_without_params_and_auth_fails(
        self, *args, **kwargs
    ):
        self.login_active_user()
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name))
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_referral_without_params_without_params_and_unauth_fails(
        self, *args, **kwargs
    ):
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name))
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GetMyReferralCodeTestCases(UserTestCases):
    """
    Authorization test cases for referral test case
    """

    fake = Faker()

    base_name = "referral"
    extended_name = "get-my-referral-code"

    def test_get_referral_code_with_auth_and_not_expired_succeeds(
        self, *args, **kwargs
    ):
        self.login_active_user()
        self.active_user.referral_code_expiry_date = timezone.now() + timedelta(days=7)
        self.active_user.save()
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name))
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_referral_code_without_auth_fails(self, *args, **kwargs):
        self.active_user.referral_code_expiry_date = timezone.now() + timedelta(days=7)
        self.active_user.save()
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name))
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_referral_code_with_expired_but_auth_succeeds(self, *args, **kwargs):
        self.login_active_user()

        old_referral_code = self.active_user.referral_code

        self.active_user.referral_code_expiry_date = timezone.now() - timedelta(days=7)
        self.active_user.save()
        response = self.client.get(
            reverse(self.get_custom_action_url(self.extended_name))
        )

        self.assertNotEqual(old_referral_code, response.data.get("referral_code", ""))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
