from django.apps import AppConfig


class MerchantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.merchants'  # Changed from just 'merchants'