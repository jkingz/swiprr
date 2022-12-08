import dateutil.parser
from copy import deepcopy

from allauth.account import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from allauth.socialaccount.models import SocialAccount
from allauth.utils import email_address_exists
from core.serializers import JSONSerializerField
from core.shortcuts import get_object_or_None
from core.utils import HomeswiprMailer
from ddf_manager.ddf_logger import logger
from dj_rest_auth.registration.serializers import SocialLoginSerializer
from dj_rest_auth.serializers import LoginSerializer, PasswordResetSerializer
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.utils.translation import ugettext_lazy as _
from requests.exceptions import HTTPError

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .mixins import HomeswiprSocialLoginHelper
from .models import (
    HomeswiprEmailAddress,
    HomeswiprLead,
    HomeswiprMail,
    Referral,
    User,
    UserRegistrationInformation,
)


class UserBasicInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name")


class ReferralSerializer(serializers.ModelSerializer):

    referred_by = UserBasicInfoSerializer()
    invited_user = UserBasicInfoSerializer()

    class Meta:
        model = Referral
        fields = ("referred_by", "invited_user", "pk")


class UserTokenExchangeFirstNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("first_name",)


class ReferralCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("referral_code",)


class UserProfileSerializer(serializers.ModelSerializer):

    referred_by = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "referred_by",
            "phone_number",
            "is_superuser",
            "is_user_manager",
            "referral_code",
            "date_joined",
            "is_agent",
            "user_type"
        )

    def get_referred_by(self, obj):
        referral = get_object_or_None(Referral.active_objects, invited_user=obj)
        return ReferralSerializer(referral, many=False).data

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(UserProfileSerializer, self).to_representation(instance)
        if instance.user_type:
            data.update({'user_type': instance.user_type.type })

        return data


class HomewSwiprPasswordResetSerializer(PasswordResetSerializer):
    def get_email_options(self):
        return {"html_email_template_name": "account/email/password_reset_email.html"}

    def validate_email(self, value):
        social_account = get_object_or_None(SocialAccount, user__email=value)
        if social_account:
            raise ValidationError(
                ['This account is signed up using a social account. Please sign in using your corresponding social application.']
            )

        user = get_object_or_None(get_user_model(), email=value)

        if not user:
            raise ValidationError(
                ['Account not found, please make sure that this account exists.']
            )

        return super().validate_email(value)


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRegistrationInformation
        fields = (
            "first_name",
            "raw_json",
            "last_name",
            "phone_number",
            "email",
            "social_application",
        )


class HomeswiprSocialLoginSerializer(HomeswiprSocialLoginHelper, SocialLoginSerializer):
    access_token = serializers.CharField(required=False, allow_blank=True)
    id_token = serializers.CharField(required=False, allow_blank=True)
    code = serializers.CharField(required=False, allow_blank=True)
    social_eula_agreement = serializers.BooleanField(default=False)
    # Sanity check on frontend
    from_sign_up_page = serializers.BooleanField(default=False)
    referral_code = serializers.CharField(required=False, write_only=True)
    json_user = JSONSerializerField(required=False, write_only=True)

    # Use in the view ot check if we need to prompt a social eula agreement
    prompt_eula_agreement = False

    def _apple_save_user_registration(self, attrs):

        raw_json = attrs.get("json_user", None)

        if raw_json:
            data = {
                "raw_json": raw_json,
                "email": raw_json.get("email"),
                "first_name": raw_json.get("name", {"firstName": ""}).get(
                    "firstName", ""
                ),
                "last_name": raw_json.get("name", {"lastName": ""}).get("lastName", ""),
                "social_application": UserRegistrationInformation.APPLE,
            }

            serializer = UserRegistrationSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
            else:
                logger.error(
                    f"Saving apple reqgistration with serializer failed with these errors: {serializer.errors}"
                )
                # If our serializer failed for some reason, we still need to save it! (Apple only passes this information once)
                # So what we do is to forcibly push the raw json to our model
                UserRegistrationInformation(
                    raw_json=raw_json,
                    social_application=UserRegistrationInformation.APPLE,
                ).save()

    def _apple_clean_up(self, login):

        # Check if we have a data on user registration information to append on our final user
        email = login.account.user.email

        # Gets all information that we have been collected
        batch_user_information = UserRegistrationInformation.objects.filter(
            email=email
        ).order_by("-date_created")

        # If there's a batch_user_information
        if batch_user_information:
            # Get the first one and use this as our base
            to_append_batch_user_information = batch_user_information[0]

            # Get all of the name
            login.account.user.first_name = to_append_batch_user_information.first_name
            login.account.user.last_name = to_append_batch_user_information.last_name
            login.account.user.save()

            for info in batch_user_information:
                # Clean all the information with this email
                info.is_active = False
                info.save()

        return login

    def validate(self, attrs):
        view = self.context.get("view")
        request = self._get_request()

        if not view:
            raise serializers.ValidationError(
                _("View is not defined, pass it as a context variable")
            )

        adapter_class = getattr(view, "adapter_class", None)
        if not adapter_class:
            raise serializers.ValidationError(_("Define adapter_class in view"))

        adapter = adapter_class(request)
        app = adapter.get_provider().get_app(request)

        if adapter.get_provider().name == "Apple":
            # Try to cache if the frontend passes a user parameter
            self._apple_save_user_registration(attrs)

        # More info on code vs access_token
        # http://stackoverflow.com/questions/8666316/facebook-oauth-2-0-code-and-token

        access_token = attrs.get("access_token")
        code = attrs.get("code")

        # Case 1: We received the access_token
        if access_token:
            tokens_to_parse = {"access_token": access_token}
            # For sign in with apple
            id_token = attrs.get("id_token")
            if id_token:
                tokens_to_parse["id_token"] = id_token

        # Case 2: We received the authorization code
        elif code:
            self.callback_url = getattr(view, "callback_url", None)
            self.client_class = getattr(view, "client_class", None)

            if not self.callback_url:
                raise serializers.ValidationError(_("Define callback_url in view"))
            if not self.client_class:
                raise serializers.ValidationError(_("Define client_class in view"))

            provider = adapter.get_provider()
            scope = provider.get_scope(request)
            client = self.client_class(
                request,
                app.client_id,
                app.secret,
                adapter.access_token_method,
                adapter.access_token_url,
                self.callback_url,
                scope,
                scope_delimiter=adapter.scope_delimiter,
                headers=adapter.headers,
                basic_auth=adapter.basic_auth,
            )
            token = client.get_access_token(code)
            access_token = token["access_token"]
            tokens_to_parse = {"access_token": access_token}

            # If available we add additional data to the dictionary
            for key in ["refresh_token", "id_token", adapter.expires_in_key]:
                if key in token:
                    tokens_to_parse[key] = token[key]
        else:
            raise serializers.ValidationError(
                _("Incorrect input. access_token or code is required.")
            )

        social_token = adapter.parse_token(tokens_to_parse)
        social_token.app = app

        try:
            login = self.get_social_login(adapter, app, social_token, access_token)

            # Sanity check for the maintainer
            # Checks if this is a registration or login
            if attrs.get("from_sign_up_page", False):
                # Checks if this account already exists
                account = deepcopy(login)
                account.lookup()

                if account.is_existing is False:
                    user_eula_agrees = attrs.get("social_eula_agreement", False)
                    if not user_eula_agrees:
                        raise serializers.ValidationError(
                            _(
                                "To sign up, you must accept the terms and policy of."
                            )
                        )
                else:
                    # Client, wants the user to be able to sign in even on the sign up page.
                    # If acocunt exists and the on the sign up page, let the user pass through
                    pass

                    # raise serializers.ValidationError(
                    #     _("User is already registered with this e-mail address.")
                    # )
            else:

                account = deepcopy(login)
                account.lookup()
                if account.is_existing is False:
                    # Trying to login without account, return a prompt and show a
                    # a checkbox for the user
                    user_eula_agrees = attrs.get("social_eula_agreement", False)
                    if not user_eula_agrees:
                        # Use in the view ot check if we need to prompt a social eula agreement
                        self.prompt_eula_agreement = True
                        raise serializers.ValidationError(
                            _(
                                "Detected creation of an account, Please accept the terms and policy of."
                            )
                        )

            self.complete_social_login(request, login, attrs.get("referral_code", ""))
        except HTTPError:
            raise serializers.ValidationError(_("Incorrect value"))

        if login.user.email == "":
            raise serializers.ValidationError(
                _("Please enable the permission to let us use your email.")
            )

        if not login.is_existing:
            # We have an account already signed up in a different flow
            # with the same email address: raise an exception.
            # This needs to be handled in the frontend. We can not just
            # link up the accounts due to security constraints
            if allauth_settings.UNIQUE_EMAIL:
                # Do we have an account already with this email address?
                account_exists = (
                    get_user_model()
                    .active_objects.filter(
                        email=login.user.email,
                    )
                    .exists()
                )
                if account_exists:
                    raise serializers.ValidationError(
                        _(
                            """We tried creating your account, but a user is already registered with this e-mail address. Please
                            sign in with your credentials!"""
                        )
                    )

            login.lookup()
            login.save(request, connect=True)

        if adapter.get_provider().name == "Apple":
            # Try to cache if the frontend passes a user parameter
            login = self._apple_clean_up(login)

        attrs["user"] = login.account.user

        return attrs


class UserSerializer(serializers.ModelSerializer):

    date_joined = serializers.DateTimeField(
        format="%B %d, %Y", input_formats=["%B %d, %Y", "iso-8601"]
    )

    class Meta:
        model = get_user_model()
        fields = (
            "pk",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "is_superuser",
            "is_user_manager",
            "referral_code",
            "date_joined",
            "is_agent",
            "agents",
            "is_active",
            "user_type"
        )
        read_only_fields = (
            "pk",
            "first_name",
            "last_name",
            "phone_number",
            "is_superuser",
            "is_user_manager",
            "referral_code",
            "date_joined",
            "fullname"
        )

    def save(self, *args, **kwargs):

        # Get old to update it or create a new one
        email, created = HomeswiprEmailAddress.objects.get_or_create(
            email=self.instance.email, user=self.instance
        )

        new_email = self.validated_data.get("email", "")

        email.email = new_email
        email.primary = True
        email.save()

        return super().save(*args, **kwargs)

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(UserSerializer, self).to_representation(instance)
        data.update({'fullname': f"{instance.first_name} {instance.last_name}"})
        agents = instance.agents.all()
        if agents:
            user = get_user_model().objects.filter(pk__in=agents).values('first_name', 'last_name', 'id', 'email')
            agents_list = list()
            for agent in user:
                agents_list.append({
                    'pk': agent.get('id'),
                    'fullname': f"{agent.get('first_name')} {agent.get('last_name')}",
                    'email': agent.get('email')
                })
            data.update({'agents': agents_list})
        if instance.user_type:
            data.update({'user_type': instance.user_type.type })

        return data


class RegisterSerializer(serializers.Serializer):
    # Overrides so that we can have a first name and last name required
    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    password1 = serializers.CharField(required=True, write_only=True)
    password2 = serializers.CharField(required=True, write_only=True)
    eula_agreement = serializers.BooleanField(default=False)
    referral_code = serializers.CharField(required=False, write_only=True)

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _("A user is already registered with this e-mail address.")
                )
        return email

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError(
                _("The two password fields didn't match.")
            )

        if not data["eula_agreement"]:
            raise serializers.ValidationError(
                _("To sign up, you must accept the terms and policy of.")
            )

        return data

    def get_cleaned_data(self):
        return {
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
            "password1": self.validated_data.get("password1", ""),
            "email": self.validated_data.get("email", ""),
            "referral_code": self.validated_data.get("referral_code", ""),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()

        adapter.save_user(request, user, self)

        # Commented to add a little note that email adresses
        # are moved to models post save.
        setup_user_email(request, user, [])

        user.save()

        referred_by = get_object_or_None(
            User, referral_code=self.cleaned_data.get("referral_code", "")
        )

        if referred_by:
            referral = Referral.objects.create(
                referred_by=referred_by, invited_user=user
            )
            referral.save()

        return user


class CustomLoginSerializer(LoginSerializer):
    """
    Custom Serializer for login
    """

    def _validate_email(self, email, password):
        check_user = get_object_or_None(HomeswiprEmailAddress, email=email)

        # Check if email exists
        if not check_user:
            # Raise a generalized error
            raise serializers.ValidationError(
                _("Unable to log in with provided credentials.")
            )

        # Check if User is verified
        if check_user.verified is False:
            raise serializers.ValidationError(
                _("User is not verified. Please verify your email.")
            )
        return super()._validate_email(email, password)


class HomeswiprLeadSerializer(serializers.ModelSerializer):

    class Meta:
        model = HomeswiprLead
        fields = "__all__"

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(HomeswiprLeadSerializer, self).to_representation(instance)
        timezone = dateutil.parser.parse(data.get('created_date'))
        date_time = timezone.strftime("%b %d %Y %H:%M:%S")
        data.update({"created_date": date_time})

        agents = instance.agents.all()
        if agents:
            user = get_user_model().objects.filter(pk__in=agents).values('first_name', 'last_name', 'id', 'email')
            agents_list = list()
            for agent in user:
                agents_list.append({
                    'pk': agent.get('id'),
                    'fullname': f"{agent.get('first_name')} {agent.get('last_name')}",
                    'email': agent.get('email')
                })
            data.update({'agents': agents_list})
        return data


class HomeswiprMailerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeswiprMail
        fields = "__all__"
