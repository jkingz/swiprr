from dj_rest_auth.registration.views import VerifyEmailView
from django.conf.urls import url
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework import routers

from .views import (
    AppleLogin,
    FacebookConnect,
    FacebookLogin,
    GoogleConnect,
    GoogleLogin,
    HomeswiprLeadViewSet,
    HomeswiprMailViewSet,
    HomeswiprUserManagerViewSet,
    LinkedInConnect,
    LinkedInLogin,
    MyUserProfileViewset,
    ReferralViewSet,
    ResendEmailViewSet,
    UserViewSet,
)

# We can't just directly register these on routers as
# the api name would be 'profile/<pk>' which is just strange.
# Instead manually register profile as http method here
profile = MyUserProfileViewset.as_view({"get": "retrieve", "patch": "partial_update"})

resend_email = ResendEmailViewSet.as_view({"post": "post"})

urlpatterns = [path("profile/", profile, name="profile")]

auth_urls = [
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/apple/", AppleLogin.as_view(), name="apple-login"),
    path("auth/facebook/", FacebookLogin.as_view(), name="fb_login"),
    path("auth/facebook/connect/", FacebookConnect.as_view(), name="fb_connect"),
    path("auth/google/", GoogleLogin.as_view(), name="google_login"),
    path("auth/google/connect/", GoogleConnect.as_view(), name="google_connect"),
    path("auth/linked_in/", LinkedInLogin.as_view(), name="linked_in_login"),
    path(
        "auth/linked_in/connect/", LinkedInConnect.as_view(), name="linked_in_connect"
    ),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    path(
        "auth/registration/resend-email-verification/",
        resend_email,
        name="rest_resend_email",
    ),
    path("accounts/", include("allauth.urls"), name="socialaccount_signup"),
    # NOTE: Don't remove this.
    # This is an official note in the documentation, looks like allauth under the hood causes some
    # unnecessary redirection when email is mandatory and this is the dj-rest-auth's
    # way of workaround
    path(
        "auth/registration/account-email-verification-sent/",
        VerifyEmailView.as_view(),
        name="account_email_verification_sent",
    ),
    # NOTE: This is the official solution for the password reset on FAQ of dj-rest-auth, BUT
    # I think by overriding the either the template or the email this could be avoided. We should do that
    # if we have time on the future.
    # Source: https://dj-rest-auth.readthedocs.io/en/latest/faq.html
    url(
        r"^password-reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        TemplateView.as_view(template_name="password_reset_confirm.html"),
        name="password_reset_confirm",
    ),
]

urlpatterns += auth_urls

router = routers.SimpleRouter()

router.register(r"", UserViewSet, basename="users")
router.register(r"referrals", ReferralViewSet, basename="referral")
# TODO: Need to combine this with the user routers.
router.register(
    r"homeswipr/admin/users", HomeswiprUserManagerViewSet, basename="users_manager"
)
router.register(r"leads", HomeswiprLeadViewSet, basename="leads")
router.register(r"mails", HomeswiprMailViewSet, basename="mails")

urlpatterns += router.urls
