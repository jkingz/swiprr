import uuid

from crea_parser.tests.factories.property import PropertyFactory
from django.urls import reverse
from homeswipr.tests.factories.property_favorite import PropertyFavoriteFactory
from rest_framework import status

from .base_app_test import CoreBaseTest


class MyFavoritePropertyTestCases(CoreBaseTest):
    """
    Authorization test cases for favorite property
    """

    not_favorited_property = None
    property_favorited_record = None
    base_name = "favorited-properties"

    # Our testing data should not go this id number
    invalid_pk = 999999

    def setUp(self, *args, **kwargs):
        # Call super here first, to set all users
        return_value = super().setUp(*args, **kwargs)

        self.not_favorited_property = PropertyFactory()

        self.property_favorited_record = PropertyFavoriteFactory(user=self.active_user)
        self.archived_favorited_record = PropertyFavoriteFactory(
            user=self.active_user, favorited_property__is_active=False
        )
        self.archived_favorited = PropertyFavoriteFactory(
            user=self.active_user, is_active=False
        )

        PropertyFactory(
            address__connected_property=self.property_favorited_record.favorited_property
        )

        return return_value

    def test_get_favorited_property_list_succeeds(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.get(reverse(self.get_list_url()), {})
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_favorited_property_list_with_uauthenticated_user_fails(
        self, *args, **kwargs
    ):
        response = self.client.get(reverse(self.get_list_url()), {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_favorited_property_with_search_text(self, *args, **kwargs):
        self.login_active_user()

        # Not a address but this should be able to search check the property list properly
        # This should avoid things like producing an address with faker that's the same with self
        # self.property_one
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
            reverse(self.get_list_url()), data={"search_text": unique_string}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 17)

    def test_post_create_favorited_property_succeeds(self, *args, **kwargs):
        self.login_active_user()

        response = self.client.post(
            reverse(self.get_list_url()),
            {"favorited_property": self.not_favorited_property.pk},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_create_favorited_property_with_unauthenticated_user_fails(
        self, *args, **kwargs
    ):
        response = self.client.post(
            reverse(self.get_list_url()),
            {"favorited_property": self.not_favorited_property.pk},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_create_favorited_property_with_no_input_fails(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.post(reverse(self.get_list_url()), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_create_favorited_property_with_invalid_pk_fails(
        self, *args, **kwargs
    ):
        self.login_active_user()
        response = self.client.post(
            reverse(self.get_list_url()), {"favorited_property": self.invalid_pk}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_create_favorited_property_duplicate_fails(self, *args, **kwargs):
        self.login_active_user()
        PropertyFavoriteFactory(
            user=self.active_user, favorited_property=self.not_favorited_property
        )
        response = self.client.post(
            reverse(self.get_list_url()),
            {"favorited_property": self.not_favorited_property.pk},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_favorited_property_with_forbidden_user_fails(self, *args, **kwargs):
        self.login_other_user()

        response = self.client.delete(
            reverse(
                self.get_detail_url(), kwargs={"pk": self.property_favorited_record.pk}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_favorited_property_succeeds(self, *args, **kwargs):
        self.login_active_user()
        response = self.client.delete(
            reverse(
                self.get_detail_url(), kwargs={"pk": self.property_favorited_record.pk}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_favorited_property_unauthenticated_fails(self, *args, **kwargs):
        response = self.client.delete(
            reverse(
                self.get_detail_url(), kwargs={"pk": self.property_favorited_record.pk}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
