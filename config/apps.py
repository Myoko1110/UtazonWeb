from django.apps import AppConfig

from config import settings


class Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'config'
    path = settings.BASE_DIR / "config"
