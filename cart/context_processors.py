from django.http import HttpRequest

from .cart import Cart


# Create context processor so our cart can work on all pages of the site
def cart(request: HttpRequest) -> dict:
    """
    Context processor to make the cart globally accessible in templates.

    Args:
        request (HttpRequest): The HTTP request object containing user and session data.

    Returns:
        dict: A dictionary containing the cart instance.
    """
    # Return the default data from our Cart
    return {'cart': Cart(request)}
