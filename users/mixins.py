from allauth.account import app_settings as account_settings
from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.utils import complete_signup, perform_login, user_username
from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount import signals
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.helpers import _add_social_account, _social_login_redirect
from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount.providers.base import AuthProcess
from core.shortcuts import get_object_or_None
from django.db.models import Q
from django.forms import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Referral, User


class ReferralHelperMixin(object):
    """
    Referral helper mixin
    """

    def filter_referral_on_name_and_email(self, queryset, search_text):
        return queryset.filter(
            Q(invited_user__first_name__icontains=search_text)
            | Q(invited_user__last_name__icontains=search_text)
            | Q(invited_user__email__icontains=search_text)
        )


class HomeswiprSocialLoginHelper(object):
    """
    Functions that overrides the social login.
    dj-rest-auth sends email verification even if on social login
    found no trace on documentation of preventing this other than
    changing the variable on settings that has "mandatory"
    which is not what we want. We want to keep the the email verifiaction
    on manual sign in and sign up. But not on the social login
    """

    def complete_social_signup(self, request, sociallogin):
        return complete_signup(
            request,
            sociallogin.user,
            False,
            sociallogin.get_redirect_url(request),
            signal_kwargs={"sociallogin": sociallogin},
        )

    def _login_social_account(self, request, sociallogin):
        return perform_login(
            request,
            sociallogin.user,
            email_verification=False,
            redirect_url=sociallogin.get_redirect_url(request),
            signal_kwargs={"sociallogin": sociallogin},
        )

    def _process_signup(self, request, sociallogin, referral_code=""):
        auto_signup = get_adapter(request).is_auto_signup_allowed(request, sociallogin)
        if not auto_signup:
            request.session["socialaccount_sociallogin"] = sociallogin.serialize()
            url = reverse("socialaccount_signup")
            ret = HttpResponseRedirect(url)
        else:
            # Ok, auto signup it is, at least the e-mail address is ok.
            # We still need to check the username though...
            if account_settings.USER_MODEL_USERNAME_FIELD:
                username = user_username(sociallogin.user)
                try:
                    get_account_adapter(request).clean_username(username)
                except ValidationError:
                    # This username is no good ...
                    user_username(sociallogin.user, "")
            # FIXME: This part contains a lot of duplication of logic
            # ("closed" rendering, create user, send email, in active
            # etc..)
            if not get_adapter(request).is_open_for_signup(request, sociallogin):
                return render(
                    request,
                    "account/signup_closed." + account_settings.TEMPLATE_EXTENSION,
                )
            get_adapter(request).save_user(request, sociallogin, form=None)
            ret = self.complete_social_signup(request, sociallogin)

        # If referral code is passed, add a referral row
        if referral_code:
            referred_by = get_object_or_None(User, referral_code=referral_code)
            if referred_by:
                referral = Referral.objects.create(
                    referred_by=referred_by, invited_user=sociallogin.user
                )
                referral.save()
        return ret

    def complete_social_login(self, request, sociallogin, referral_code=""):

        assert not sociallogin.is_existing
        sociallogin.lookup()
        try:
            get_adapter(request).pre_social_login(request, sociallogin)
            signals.pre_social_login.send(
                sender=SocialLogin, request=request, sociallogin=sociallogin
            )
            process = sociallogin.state.get("process")
            if process == AuthProcess.REDIRECT:
                return _social_login_redirect(request, sociallogin)
            elif process == AuthProcess.CONNECT:
                return _add_social_account(request, sociallogin)
            else:
                return self._complete_social_login(request, sociallogin, referral_code)
        except ImmediateHttpResponse as e:
            return e.response

    def _complete_social_login(self, request, sociallogin, referral_code=""):
        if request.user.is_authenticated:
            get_account_adapter(request).logout(request)
        if sociallogin.is_existing:
            # Login existing user
            ret = self._login_social_account(request, sociallogin)
            signals.social_account_updated.send(
                sender=SocialLogin, request=request, sociallogin=sociallogin
            )
        else:
            # New social user
            ret = self._process_signup(request, sociallogin, referral_code)
        return ret
