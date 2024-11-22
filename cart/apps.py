from django.apps import AppConfig


class CartConfig(AppConfig):
    """
    Configuration class for the 'cart' application.

    This class defines application-specific settings and behavior for the 'cart' app.
    It ensures that Django's AppConfig system knows how to set up this application.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cart'
