from django.apps import AppConfig


class DealConfig(AppConfig):
    name = 'deal'

    def ready(self):
        from .signals import DealsSignal
