import json

from allauth.account.utils import send_email_confirmation
from allauth.socialaccount.providers.apple.client import AppleOAuth2Client
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.linkedin_oauth2.views import LinkedInOAuth2Adapter
from core.pagination import AutoCompleteSetPagination, StandardResultsSetPagination
from core.shortcuts import get_object_or_403
from core.permissions import IsMortgageBroker
from dj_rest_auth.registration.views import SocialConnectView, SocialLoginView
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Max, Q, query
from django.shortcuts import get_object_or_404
from django.utils import timezone
from homeswipr.mixins import FavoriteHelperMixin, PropertyHelperMixin
from homeswipr.models import Property, PropertyFavorite, PropertyInquiry
from homeswipr.serializers import PropertyFavoriteSerializer, PropertySerializer
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import HomeswiprLead, HomeswiprMail, Referral, User, UserHistory
from rest_framework.exceptions import PermissionDenied

from core.permissions import IsAgentUser, IsAdmin, IsMortgageBroker, IsSalesAgent
from .mixins import ReferralHelperMixin
from .models import HomeswiprEmailAddress, UserType
from .permissions import RetrieveReferralAsOwnerOrUserManagerPermission
from .serializers import (
    HomeswiprLeadSerializer,
    HomeswiprMailerSerializer,
    HomeswiprSocialLoginSerializer,
    ReferralCodeSerializer,
    ReferralSerializer,
    UserSerializer,
    UserProfileSerializer,
    UserTokenExchangeFirstNameSerializer,
)


class FacebookLogin(SocialLoginView):
    serializer_class = HomeswiprSocialLoginSerializer
    adapter_class = FacebookOAuth2Adapter

    def post(self, request, *args, **kwargs):

        # Overrides the post on the library to avoid
        # exception true and return the prompt that was
        # detected on the serializer
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)

        if self.serializer.is_valid():
            self.login()
            return self.get_response()
        else:
            # Handle error manually to stick prompt eula agreement
            response = Response(
                self.serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
            response.data[
                "prompt_eula_agreement"
            ] = self.serializer.prompt_eula_agreement
            return response


class FacebookConnect(SocialConnectView):
    adapter_class = FacebookOAuth2Adapter


class AppleLogin(SocialLoginView):
    adapter_class = AppleOAuth2Adapter
    client_class = AppleOAuth2Client
    callback_url = settings.APPLE_CALLBACK_URL
    serializer_class = HomeswiprSocialLoginSerializer

    def post(self, request, *args, **kwargs):

        # Overrides the post on the library to avoid
        # exception true and return the prompt that was
        # detected on the serializer
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)

        if self.serializer.is_valid():
            self.login()
            return self.get_response()
        else:
            # Handle error manually to stick prompt eula agreement
            response = Response(
                self.serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
            response.data[
                "prompt_eula_agreement"
            ] = self.serializer.prompt_eula_agreement
            return response


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter


class GoogleConnect(SocialConnectView):
    adapter_class = GoogleOAuth2Adapter


class LinkedInLogin(SocialLoginView):
    adapter_class = LinkedInOAuth2Adapter


class LinkedInConnect(SocialConnectView):
    adapter_class = LinkedInOAuth2Adapter


class MyUserProfileViewset(
    viewsets.GenericViewSet, RetrieveModelMixin, UpdateModelMixin
):
    """
    The class for user profile viewsets.
    E.g: Fetching and updating the user detail

    # NOTE: We might want to combine this and HomeswiprUserManagerViewSet
    to have a single viewset that is relevant to users
    """

    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, *args, **kwargs):
        # No user == deny the user
        return get_object_or_403(get_user_model(), pk=self.request.user.pk)

    def get_object(self):
        # This should remove the default lookup field for pk on retrieve,
        # without changing how the viewset behaves
        return self.get_queryset()


class UserViewSet(viewsets.GenericViewSet, UpdateModelMixin):
    """
    The class is for User viewset.
    """

    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (
        IsAuthenticated,
    )
    queryset = get_user_model().active_objects.all()

    def get_queryset(self, *args, **kwargs):
        user_payload = {}
        user_search_text = self.request.query_params.get("search_text", "")
        users = self.request.query_params.get("users", "")

        if users:
            user_payload.update({'id__in': json.loads(users)})

        list_of_user = self.queryset.filter(**user_payload)

        if user_search_text:
            list_of_user = list_of_user.filter(
                Q(first_name__icontains=user_search_text)
                | Q(last_name__icontains=user_search_text)
                | Q(email__icontains=user_search_text)
            ).order_by("-pk")

        return list_of_user

    @action(detail=False, methods=["get"])
    def clients(self, *args, **kwargs):
        queryset = self.get_queryset().filter(Q(is_agent=False)|Q(is_user_manager=False))
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def agents(self, *args, **kwargs):
        queryset = self.get_queryset().filter(is_agent=True)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["put"])
    def deactivate_user(self, *args, **kwargs):
        params = self.request.data.get('params')
        user = get_object_or_404(User, pk=params.get('pk'))
        user.is_active = params.get('is_active')
        user.save()

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def mortgage_broker(self, *args, **kwargs):
        queryset = self.get_queryset().filter(user_type__type='Mortgage Broker')
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def sales_agent(self, *args, **kwargs):
        queryset = self.get_queryset().filter(user_type__type='Sales Agent')
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ReferralViewSet(
    viewsets.GenericViewSet, ListModelMixin, RetrieveModelMixin, ReferralHelperMixin
):
    """
    The viewset for a referral
    """

    queryset = Referral.active_objects.all().order_by("-date_created")
    serializer_class = ReferralSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (
        IsAuthenticated,
        RetrieveReferralAsOwnerOrUserManagerPermission,
    )

    def list(self, *args, **kwargs):

        search_text = self.request.query_params.get("search_text", "")

        # Make this queryset limit to the user only
        self.queryset = self.queryset.filter(referred_by=self.request.user)

        # Overide queryset to include a search text
        self.queryset = self.filter_referral_on_name_and_email(
            self.queryset, search_text
        )

        return super().list(*args, **kwargs)

    # Converts the token to first name
    # A public api, should only return the first name and not sensitive data!
    @action(
        detail=False,
        methods=["get"],
        serializer_class=UserTokenExchangeFirstNameSerializer,
        permission_classes=(),
    )
    def convert_token_to_first_name(self, *args, **kwargs):

        user = get_object_or_404(
            get_user_model(),
            referral_code=self.request.query_params.get("referral_code", ""),
            referral_code_expiry_date__gte=timezone.now(),
        )

        serializer = self.get_serializer(user, many=False)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], serializer_class=ReferralCodeSerializer)
    def get_my_referral_code(self, *args, **kwargs):

        user = get_object_or_404(get_user_model(), pk=self.request.user.pk)

        if user.is_referral_code_expired:
            user.generate_referral_code()
            user.save()

        serializer = self.get_serializer(user, many=False)
        return Response(serializer.data)


class HomeswiprUserManagerViewSet(
    viewsets.GenericViewSet,
    RetrieveModelMixin,
    UpdateModelMixin,
    ListModelMixin,
    FavoriteHelperMixin,
    ReferralHelperMixin,
    PropertyHelperMixin,
):
    """
    The viewset for the user manager. (Admin who can manage the user)

    NOTE: We might want to combine this and MyUserProfileViewset
    to have a single viewset that is relevant to users and
    separate the different properties to their respective
    viewset. E.g: user_list_of_favorites to FavoriteViewSet

    NOTE: That this is not a model viewset, we currently
    have the creation of user on registration part
    """

    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination
    # We want the default list, update, and retrieve to be only accessible
    # by the user manager
    permission_classes = (
        IsAuthenticated,
    )
    queryset = get_user_model().active_objects.all()

    # Allows order by
    filter_backends = [filters.OrderingFilter]
    ordering = "first_name"
    ordering_fields = [
        "pk",
        "email",
        "first_name",
        "last_name",
        "date_joined",
        "is_user_manager",
        "is_superuser",
        "is_agent",
    ]

    def get_queryset(self, *args, **kwargs):
        user = self.request.user

        user_search_text = self.request.query_params.get("user_search_text", "")

        list_of_user = get_user_model().active_objects.all()
        list_of_user = list_of_user.filter(
            Q(first_name__icontains=user_search_text)
            | Q(last_name__icontains=user_search_text)
            | Q(email__icontains=user_search_text)
        ).order_by("-pk")

        if (user.is_authenticated and user.is_agent):
            list_of_user =  list_of_user.filter(
                Q(agents__id=user.id)|
                Q(id=user.id)
            )
        return list_of_user

    @action(detail=True, methods=["get"], serializer_class=PropertyFavoriteSerializer)
    def user_list_of_favorites(self, request, pk=None):

        search_text = self.request.query_params.get("search_text", "")

        user = self.get_object()

        queryset = PropertyFavorite.active_objects.filter(
            user=user, favorited_property__is_active=True
        ).order_by("-pk")

        queryset = self.filter_favorite_by_address(queryset, search_text)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], serializer_class=ReferralSerializer)
    def referrals(self, request, pk=None):

        search_text = self.request.query_params.get("search_text", "")

        user = self.get_object()

        queryset = Referral.active_objects.filter(referred_by=user).order_by(
            "-date_created"
        )

        # Overide queryset to include a search text
        queryset = self.filter_referral_on_name_and_email(queryset, search_text)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], serializer_class=PropertySerializer)
    def user_recently_viewed(self, request, pk=None):
        search_text = self.request.query_params.get("search_text", "")
        user = self.get_object()

        # Annotate should pull the date created and put the max (latest)
        # to our property table
        queryset = (
            Property.active_objects.filter(
                user_history__user=user, user_history__history_type=UserHistory.VIEWED
            )
            .select_related("Address", "Building", "Info", "land")
            .annotate(created=Max("user_history__date_created"))
            .order_by("-created")
            .distinct()
        )

        queryset = self.filter_property_by_keyword(queryset, search_text)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], serializer_class=UserProfileSerializer)
    def user_manager_and_superuser(self, request):
        list_of_user = get_user_model().active_objects.filter(is_active=True)
        queryset = list_of_user.filter(
            Q(is_user_manager=True) | Q(is_staff=True) | Q(is_superuser=True)
        ).order_by("-pk")
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    @action(detail=False, methods=["post"], serializer_class=UserProfileSerializer)
    def user_update_role(self, request, pk=None):
        list_of_user = get_user_model().active_objects.filter(is_active=True)
        default = request.data.copy()
        try:
            user = list_of_user.get(id=default.get("pk"))
            user_type = default.get("user_type", None)
            user_type_instance = None

            if user_type:
               user_type_instance = UserType.objects.get(type=user_type)


            if not user.is_superuser:
                # NOTE: No one should be able to update the superuser
                user.is_user_manager = default.get("is_user_manager", user.is_user_manager)
                user.is_agent = default.get("is_agent", user.is_agent)
                user.user_type = user_type_instance
                user.save()
                serializer = self.get_serializer(user)
            else:
                raise PermissionDenied({"message":"You don't have permission to access",
                                         "email": user.email})

            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:

            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"], name="Assign agent")
    def assign_agent(self, request, pk=None):
        agents = request.data.get("agents", None)
        queryset = self.get_queryset()
        emails = [agent.get('email') for agent in agents]
        try:
            # Assign agents on actual user.
            user = queryset.get(pk=int(pk))
            for agent in agents:
                agent_instance = get_user_model().objects.get(email=agent.get('email'))
                user.agents.add(agent_instance)

            # To remove agent on User.
            to_remove = user.agents.exclude(email__in=emails)
            if to_remove:
                for agent in to_remove:
                    user.agents.remove(agent)

            # Property Offer Operation
            # property_offer_buyers = PropertyOffer.objects.filter(property_offer_buyer__user=user)
            # if property_offer_buyers:
            #     for property_offer_buyer in property_offer_buyers:
            #         offer = property_offer_buyer.property_offer
            #         # Assign agents on Property Offer.
            #         for agent in agents:
            #             agent_instance = get_user_model().objects.get(email=agent.get('email'))
            #             offer.agents.add(agent_instance)
            #
            #         to_remove = offer.agents.exclude(email__in=emails)
            #         if to_remove:
            #             for agent in to_remove:
            #                 offer.agents.remove(agent)

            # HomeswiprLeads Operation
            property_inquiries = PropertyInquiry.objects.filter(user=user)
            if property_inquiries:
                for property_inquiry in property_inquiries:
                    for agent in agents:
                        agent_instance = get_user_model().objects.get(email=agent.get('email'))
                        property_inquiry.agents.add(agent_instance)

                    to_remove = property_inquiry.agents.exclude(email__in=emails)
                    if to_remove:
                        for agent in to_remove:
                            property_inquiry.agents.remove(agent)

            # Deals Operation
            # TODO: Find a way to assign an agent to a deal instance,
            # Currently due to complexity on the structure it's hard to assign an agent via the user list.

        except get_user_model().DoesNotExist:
            return Response(
                {"detail": "Assigned to value is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = self.get_serializer(user).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def user_update_detail(self, request, *args, **kwargs):
        if bool(self.request.user.is_authenticated and (self.request.user.is_user_manager or self.request.user.is_superuser)):
            user_to_update = get_object_or_404(get_user_model(), pk=kwargs.get('pk'))
            user_to_update.first_name = self.request.data.get('first_name')
            user_to_update.last_name = self.request.data.get('last_name')
            user_to_update.phone_number = self.request.data.get('phone_number')
            user_to_update.save()
        else:
            raise Exception("You do not have permission to update the user details.")
        return Response(status=status.HTTP_200_OK)


class ResendEmailViewSet(viewsets.GenericViewSet):
    """
    The viewset that lets the user resend an email verification

    This is needed for dj-rest-auth
    """

    # Since the user doesn't have any token currently, let the api
    # be accesed by anyone
    permission_classes = [AllowAny]

    def post(self, request):

        user = get_object_or_404(get_user_model(), email=request.data.get("email", ""))
        email = HomeswiprEmailAddress.objects.filter(user=user, verified=True).exists()

        if email:
            return Response(
                {"message": "This email is already verified"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            try:
                use_signup_template = True
                send_email_confirmation(request, user, use_signup_template)
                return Response(
                    {"message": "Email confirmation sent"},
                    status=status.HTTP_201_CREATED,
                )
            except APIException:
                return Response(
                    {
                        "message": "This email does not exist, please create a new account"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )


class HomeswiprLeadViewSet(viewsets.ModelViewSet):

    serializer_class = HomeswiprLeadSerializer
    queryset = HomeswiprLead.objects.all().order_by("-id")
    pagination_class = None
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        if (user.is_authenticated and user.is_agent):
            queryset = self.queryset.filter(agents__id=user.id)
        return queryset

    @action(detail=True, methods=["post"])
    def assign_agent(self, request, pk=None):
        agents = request.data.get('agents')
        queryset = self.queryset
        emails = [agent.get('email') for agent in agents]
        try:
            lead = queryset.get(pk=int(pk))
            for agent in agents:
                user = get_user_model().objects.get(email=agent.get('email'))
                lead.agents.add(user)
            # list of agents to be removed.
            to_remove = lead.agents.exclude(email__in=emails)
            if to_remove:
                for agent in to_remove:
                    lead.agents.remove(agent)
        except HomeswiprLead.DoesNotExist:
            return Response(
                {"detail": "assigned_to value is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = self.get_serializer(lead).data
        return Response(data, status=status.HTTP_200_OK)

class HomeswiprMailViewSet(viewsets.ModelViewSet):

    serializer_class = HomeswiprMailerSerializer
    queryset = HomeswiprMail.objects.all().order_by("-id")
    pagination_class = None

    @action(detail=True, methods=["get"], serializer_class=HomeswiprMailerSerializer)
    def get_emails(self, request, pk=None):
        mails = self.queryset.filter(email__id=int(pk))
        data = self.get_serializer(mails, many=True).data
        return Response(data, status=status.HTTP_200_OK)
