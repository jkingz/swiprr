from django.urls import reverse
from faker import Faker
from rest_framework import status

from .base_app_test import UserTestCases


class SignInTestCases(UserTestCases):
    """
    Authorization test cases for profile test case
    """

    fake = Faker()

    base_name = "rest_login"
    login_valid_data = {}
    login_invalid_data = {}

    def setUp(self, *args, **kwargs):

        val = super().setUp(*args, **kwargs)

        # The extra valid word should make this always unique
        self.login_valid_data = {
            "email": self.active_user.email,
            "password": self.default_password,
        }

        return val

    def test_post_login_success(self, *args, **kwargs):

        # Login a valid data
        response = self.client.post(reverse(self.get_root_url()), self.login_valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_login_with_wrong_password_fails(self, *args, **kwargs):

        # Login with wrong password
        response = self.client.post(
            reverse(self.get_root_url()),
            {"email": self.active_user.email, "password": "random"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_login_with_wrong_email_fails(self, *args, **kwargs):

        # Login with wrong email

        response = self.client.post(
            reverse(self.get_root_url()),
            {
                "email": f"{self.fake.first_name()}{self.fake.last_name()}@{self.fake.free_email_domain()}".lower(),
                "password": self.default_password,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_empty_login_fails(self, *args, **kwargs):

        response = self.client.post(
            reverse(self.get_root_url()), {"email": "", "password": ""}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
