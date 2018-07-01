from django.apps import AppConfig


class NotifierConfig(AppConfig):
    name = 'notifier'

    def ready(self):
        from . import signals
