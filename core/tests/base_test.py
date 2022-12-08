# Creating the base for our all tests across the app
from django.contrib.auth import get_user_model
from django_redis import get_redis_connection
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from users.tests.factories.user import UserFactory


class BaseWebTestCases(APITestCase):
    """
    The base for all our testcases, currently houses the user creation
    """

    default_password = "password"

    active_user = None
    super_user = None
    other_user = None
    staff_user = None
    users_manager_user = None

    access_token = ""

    user_model = get_user_model()

    # Simulating a request
    client = APIClient()

    def setUp(self, *args, **kwargs):
        """
        Creating an active user
        Note, we are using the funciton 'create user' so that the password will be hashed
        """
        self.super_user = UserFactory(is_admin=True)
        self.staff_user = UserFactory(is_staff=True)
        self.users_manager_user = UserFactory(is_user_manager=True)
        self.active_user = UserFactory()
        self.other_user = UserFactory()

    def login(self, email, password=None):
        if not password:
            password = self.default_password

        response = self.client.post(
            reverse("rest_login"), {"email": email, "password": password}
        )
        self.access_token = response.data.get("access_token")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def login_users_manager_user(self):
        """
        Logins a user manager
        """
        self.login(self.users_manager_user.email)

    def login_active_user(self):
        """
        Logins an active user to our client
        """
        self.login(self.active_user.email)

    def login_other_user(self):
        """
        Logins as other user to test permissions
        """
        self.login(self.other_user.email)

    def login_super_user(self):
        """
        Logins super user
        """
        self.login(self.super_user.email)

    def login_staff_user(self):
        """
        Logins staff user
        """
        self.login(self.staff_user.email)

    def _get_app_and_base_name(self):
        """
        Gets the root url of a viewset
        """
        if self.app_name:
            return f"{self.app_name}:{self.base_name}"
        return self.base_name

    def get_list_url(self):
        """
        Gets the app name with the view name and append it with list
        """
        return f"{self._get_app_and_base_name()}-list"

    def get_detail_url(self):
        """
        Gets the app name with the view name and append it with detail
        """
        return f"{self._get_app_and_base_name()}-detail"

    def get_custom_action_url(self, custom_action):
        """
        Gets the app name with the view name and append it with custom_action
        """
        return f"{self._get_app_and_base_name()}-{custom_action}"

    def get_root_url(self):
        return f"{self._get_app_and_base_name()}"

    def tearDown(self):
        get_redis_connection("default").flushall()
