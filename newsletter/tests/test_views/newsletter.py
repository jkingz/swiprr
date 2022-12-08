from django.core.files.base import ContentFile
from django.urls import reverse
from factory.django import ImageField
from faker import Faker
from newsletter.tests.factories.newsletter import NewsLetterFactory
from newsletter.tests.shortcuts import produce_valid_tags
from rest_framework import status

from .base_app_test import NewsLetterBaseTest


class NewsLetterTestCases(NewsLetterBaseTest):
    """
    Authorization test cases for profile test case
    """

    fake = Faker()
    news_letter_valid_data = {}
    news_letter_invalid_data = {}

    base_name = "newsletter"
    newsletter_one = None
    newsletter_without_tags = None

    def setUp(self, *args, **kwargs):
        self.newsletter_one = NewsLetterFactory()
        self.newsletter_without_tags = NewsLetterFactory(tags="")

        self.news_letter_valid_data = {
            "title": self.fake.sentence(),
            "body": self.fake.paragraph(),
            "image": lambda _: ContentFile(
                ImageField()._make_data({"width": 1024, "height": 768}), "example.jpg"
            ),
            "tags": produce_valid_tags(),
        }

        self.news_letter_invalid_data = {
            "title": None,
            "body": None,
            "image": "This is a picture",
            "tags": [],
        }

        return super().setUp(*args, **kwargs)

    def test_get_list_newsletter_succeeds(self, *args, **kwargs):
        # valid data
        self.login_active_user()
        response = self.client.get(reverse(self.get_list_url()), {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list_newsletter_with_unauthenticated_credentials_succeeds(
        self, *args, **kwargs
    ):
        # Newsletter should be seen even if the user is not logged in
        response = self.client.get(reverse(self.get_list_url()), {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_retrieve_newsletter_details_with_auth_succeeds(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.get(
            reverse(self.get_detail_url(), kwargs={"pk": self.newsletter_one.pk}), {}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_retrieve_newsletter_details_without_auth_succeeds(
        self, *args, **kwargs
    ):
        response = self.client.get(
            reverse(self.get_detail_url(), kwargs={"pk": self.newsletter_one.pk}), {}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_retrieve_newsletter_details_without_tags_succeeds(
        self, *args, **kwargs
    ):
        response = self.client.get(
            reverse(
                self.get_detail_url(), kwargs={"pk": self.newsletter_without_tags.pk}
            ),
            {},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_create_newsletter_with_auth_succeeds(self, *args, **kwargs):
        self.login_staff_user()
        response = self.client.post(
            reverse(self.get_list_url()), self.news_letter_valid_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
