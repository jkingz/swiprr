from core.mixins import FrontendUrlConstructionMixin
from django import template

register = template.Library()


def get_frontend_reset_confirm_url(uid, token):
    return FrontendUrlConstructionMixin().get_account_reset_password_url(uid, token)


register.filter("get_frontend_reset_confirm_url", get_frontend_reset_confirm_url)
