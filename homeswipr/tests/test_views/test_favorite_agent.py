from crea_parser.tests.factories.agent import AgentFactory
from django.urls import reverse
from homeswipr.tests.factories.agent_favorite import AgentFavoriteFactory
from rest_framework import status

from .base_app_test import CoreBaseTest


class MyFavoriteAgentTestCases(CoreBaseTest):
    """
    Authorization test cases for favorit agent
    """

    not_favorited_agent = None
    agent_favorite_record = None
    base_name = "favorited-agents"

    # Our testing data should not go this id number
    invalid_pk = 999999

    def setUp(self, *args, **kwargs):
        # Call super here first, to set all users
        return_value = super().setUp(*args, **kwargs)

        self.not_favorited_agent = AgentFactory()
        self.agent_favorite_record = AgentFavoriteFactory(user=self.active_user)

        self.archived_favorited_record = AgentFavoriteFactory(
            user=self.active_user, favorited_agent__is_active=False
        )
        self.archived_favorited = AgentFavoriteFactory(
            user=self.active_user, is_active=False
        )

        return return_value

    def test_get_favorited_agent_list_succeeds(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.get(reverse(self.get_list_url()), {})
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_favorited_agent_list_with_uauthenticated_user_fails(
        self, *args, **kwargs
    ):
        response = self.client.get(reverse(self.get_list_url()), {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_create_favorited_agent_succeeds(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.post(
            reverse(self.get_list_url()),
            {"favorited_agent": self.not_favorited_agent.pk},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_create_favorited_agent_with_unauthenticated_user_fails(
        self, *args, **kwargs
    ):
        response = self.client.post(
            reverse(self.get_list_url()),
            {"favorited_agent": self.not_favorited_agent.pk},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_create_favorited_agent_with_invalid_pk_fails(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.post(
            reverse(self.get_list_url()), {"favorited_agent": self.invalid_pk}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_create_favorited_agent_with_no_input_fails(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.post(reverse(self.get_list_url()), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_create_favorited_agent_duplicate_fails(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.post(
            reverse(self.get_list_url()), {"favorited_agent": self.invalid_pk}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_favorited_agent_with_forbidden_user_fails(self, *args, **kwargs):
        self.login_other_user()

        response = self.client.delete(
            reverse(self.get_detail_url(), kwargs={"pk": self.agent_favorite_record.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_favorited_agent_succeeds(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.delete(
            reverse(self.get_detail_url(), kwargs={"pk": self.agent_favorite_record.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_favorited_agent_unauthenticated_fails(self, *args, **kwargs):
        response = self.client.delete(
            reverse(self.get_detail_url(), kwargs={"pk": self.agent_favorite_record.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
