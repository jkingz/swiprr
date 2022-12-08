from django.urls import reverse
from rest_framework import status

from .base_app_test import CreaParserBaseTest


class CreaParserTestCases(CreaParserBaseTest):
    """
    Authorization test cases for the manual fetch

    NOTE: Tried revoking the task after running the celery
    but due to this open bug, some task can't be revoked
    # https://github.com/celery/celery/issues/4300
    """

    base_name = "crea-parser"

    def test_get_logs_with_super_credentials_succeeds(self, *args, **kwargs):
        self.login_super_user()

        response = self.client.get(reverse(self.get_list_url()), {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_logs_with_unauthenticated_credentials_fails(self, *args, **kwargs):
        response = self.client.get(reverse(self.get_list_url()), {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_logs_with_normal_user_fails(self, *args, **kwargs):
        self.login_active_user()

        response = self.client.get(reverse(self.get_list_url()), {})

        # Find another workaround on revoking the celery task
        # when we have the time
        # The revoke function freezes machine that uses wsl.
        # It works fine on pure ubuntu.
        # self.revoke_all_celery_task()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_manual_fetch_with_super_credentials_succeeds(self, *args, **kwargs):
        self.login_super_user()
        response = self.client.post(reverse(self.get_list_url()), {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_manual_fetch_with_unauthenticated_credentials_fails(
        self, *args, **kwargs
    ):

        response = self.client.post(reverse(self.get_list_url()), {})

        # Find another workaround on revoking the celery task
        # when we have the time
        # The revoke function freezes machine that uses wsl.
        # It works fine on pure ubuntu.
        # self.revoke_all_celery_task()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_manual_fetch_with_normal_user_fails(self, *args, **kwargs):

        self.login_active_user()
        response = self.client.post(reverse(self.get_list_url()), {})

        # Find another workaround on revoking the celery task
        # when we have the time
        # The revoke function freezes machine that uses wsl.
        # It works fine on pure ubuntu.
        # self.revoke_all_celery_task()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
