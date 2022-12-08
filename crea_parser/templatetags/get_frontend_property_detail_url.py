from core.mixins import FrontendUrlConstructionMixin
from django import template

register = template.Library()


def get_frontend_property_detail_url(pk):
    return FrontendUrlConstructionMixin().get_property_detail_url(pk)


register.filter("get_frontend_property_detail_url", get_frontend_property_detail_url)
