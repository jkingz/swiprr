from django.conf import settings
from rest_framework import status
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.response import Response


class HomeswiprCreateModelMixin(CreateModelMixin):
    """
    A customize mixin that overrrides the Create Model Mixin
    to reuse codes like passing to the serializer the request method
    """

    def create_with_passed_requests_on_serializer(self, *args, **kwargs):
        """
        This function just passes the request to the serializer and mimics
        the create function of the create model mixin.

        TLDR: Just adds the request as context to our serializer
        """
        serializer = self.get_serializer(
            data=self.request.data, context={"request": self.request}
        )

        if serializer.is_valid():
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DestroyArchiveModelMixin(DestroyModelMixin):
    """
    Perfroms inactive destroy mixin
    """

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Successfully archived!"}, status=status.HTTP_200_OK)


class FrontendUrlConstructionMixin(object):
    """
    Collect all frontend url construction url until
    we can find a better way to implement it
    """

    frontend_base_url = f"{settings.FRONTEND_DOMAIN}"

    def get_activation_url(self, key):
        # Activiation url email for newly signup users
        return f"{self.get_base_url()}registration/verify-email/{key}"

    def get_property_detail_url(self, pk):
        return f"{self.get_base_url()}property/{pk}"

    def get_base_url(self):
        if self.frontend_base_url.endswith("/"):
            self.frontend_base_url = self.frontend_base_url[:-1]

        if settings.HISTORY_MODE:
            return f"{self.frontend_base_url}/"
        return f"{self.frontend_base_url}/#/"

    def get_account_reset_password_url(self, uid, token):
        return f"{self.get_base_url()}forgot-password-confirm/{uid}/{token}"
