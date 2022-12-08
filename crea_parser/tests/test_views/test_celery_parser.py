from django.urls import reverse
from rest_framework import status

from .base_app_test import CreaParserBaseTest


class CreaCeleryTestCases(CreaParserBaseTest):
    """
    Authorization test cases for crea async tasks

    Find a way to test the crea parser themselves
    """

    base_name = "crea-celery"
    cancel_extended_name = "cancel"

    def test_get_async_running_tasks_with_super_user_succeeds(self, *args, **kwargs):
        self.login_super_user()

        response = self.client.get(reverse(self.get_list_url()), {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_async_running_tasks_with_unauthenticated_credentials_fails(
        self, *args, **kwargs
    ):
        response = self.client.get(reverse(self.get_list_url()), {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_async_running_tasks_with_normal_user_fails(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.get(reverse(self.get_list_url()), {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_async_running_tasks_with_staff_user_fails(self, *args, **kwargs):
        self.login_staff_user()

        response = self.client.get(reverse(self.get_list_url()), {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_cancel_async_running_tasks_with_super_user_succeeds(
        self, *args, **kwargs
    ):
        self.login_super_user()

        celery_response = self.client.post(
            reverse(self.get_custom_action_url(self.cancel_extended_name)), {}
        )
        self.assertEqual(celery_response.status_code, status.HTTP_200_OK)

    def test_post_cancel_async_running_tasks_with_unauthenticated_credentials_fails(
        self, *args, **kwargs
    ):

        celery_response = self.client.post(
            reverse(self.get_custom_action_url(self.cancel_extended_name)), {}
        )
        self.assertEqual(celery_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_cancel_async_running_tasks_with_normal_user_fails(
        self, *args, **kwargs
    ):

        self.login_active_user()

        celery_response = self.client.post(
            reverse(self.get_custom_action_url(self.cancel_extended_name)), {}
        )
        self.assertEqual(celery_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_cancel_async_running_tasks_with_staff_user_fails(
        self, *args, **kwargs
    ):

        self.login_staff_user()

        celery_response = self.client.post(
            reverse(self.get_custom_action_url(self.cancel_extended_name)), {}
        )
        self.assertEqual(celery_response.status_code, status.HTTP_403_FORBIDDEN)
