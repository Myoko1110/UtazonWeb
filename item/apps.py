from django.apps import AppConfig

from config import settings


class ItemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'item'
    path = settings.BASE_DIR / "item"
