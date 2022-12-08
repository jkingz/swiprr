from django.urls import reverse
from faker import Faker
from rest_framework import status

from .base_app_test import UserTestCases


class ProfileTestCases(UserTestCases):
    """
    Authorization test cases for profile test case
    """

    fake = Faker()
    profile_valid_data = {}

    base_name = "profile"

    def setUp(self, *args, **kwargs):

        # The extra valid word should make this always unique
        self.profile_valid_data = {
            "first_name": self.fake.first_name(),
            "last_name": self.fake.last_name(),
            "email": f"{self.fake.first_name()}{self.fake.last_name()}@{self.fake.free_email_domain()}".lower(),
        }

        self.profile_invalid_data = {"email": f"{self.fake.first_name()}"}

        return super().setUp(*args, **kwargs)

    def test_get_profile_succeeds(self, *args, **kwargs):
        # valid data
        self.login_active_user()
        response = self.client.get(reverse(self.get_root_url()), {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_profile_with_unauthenticated_credentials_fails(self, *args, **kwargs):
        response = self.client.get(reverse(self.get_root_url()), {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_succeeds(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.patch(
            reverse(self.get_root_url()), self.profile_valid_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_with_unauthenticated_credentials_fails(self, *args, **kwargs):
        response = self.client.patch(
            reverse(self.get_root_url()), self.profile_valid_data
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_with_invalid_data_fails(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.patch(
            reverse(self.get_root_url()), self.profile_invalid_data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_with_empty_data_fails(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.patch(reverse(self.get_root_url()), {})
        # This should still go through. We are using partial patch from the Update DRF
        self.assertEqual(response.status_code, status.HTTP_200_OK)
