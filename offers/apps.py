from django.apps import AppConfig


class OffersConfig(AppConfig):
    name = 'offers'

    def ready(self):
        from .signals import OffersSignal
