from django.apps import AppConfig

from config import settings

class BuyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'buy'
    path = settings.BASE_DIR / "buy"
