from django.apps import AppConfig


class PrideConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pride'

    def ready(self):
        from .scheduler import start
        start()
