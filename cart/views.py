from django.shortcuts import render, get_object_or_404
from .cart import Cart
from django.apps import apps
# from store.models import Product
from django.http import JsonResponse, HttpRequest
from django.contrib import messages

model_product = apps.get_model('store', 'Product')


def cart_summary(request: HttpRequest) -> JsonResponse:
    """
    Displays the cart summary page, showing products, quantities, and the total cost.

    Args:
        request (HttpRequest): The HTTP request object containing user and session data.

    Returns:
        HttpResponse: Renders the cart summary page with product details.
    """
    # Get the cart
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()
    return render(request, 'cart_summary.html',
                  {"cart_products": cart_products, "quantities": quantities, "totals": totals})


def cart_add(request: HttpRequest) -> JsonResponse:
    """
     Adds a product to the cart and sends a success or error message.

     Args:
         request (HttpRequest): The HTTP request containing product details in POST data.

     Returns:
         JsonResponse: A JSON response containing the updated cart quantity or an error message.
     """
    cart = Cart(request)

    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))

        product = get_object_or_404(model_product, id=product_id)

        # Try adding the product to the cart
        if not cart.add(product=product, quantity=product_qty):
            # Max quantity exceeded, show error message
            messages.error(request, "Maximum quantity for this product has been reached.")
            return JsonResponse({'error': "Max quantity exceeded"})

        # Get Cart Quantity
        cart_quantity = cart.__len__()

        # Send success response
        response = JsonResponse({'qty': cart_quantity})
        messages.success(request, "Product added to the cart.")
        return response


def cart_delete(request: HttpRequest) -> JsonResponse:
    """
    Deletes a product from the cart and sends a success message.

    Args:
        request (HttpRequest): The HTTP request containing product details in POST data.

    Returns:
        JsonResponse: A JSON response indicating the deleted product and updated cart state.
    """
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        # Get stuff
        product_id = int(request.POST.get('product_id'))
        # Call delete Function in Cart
        cart.delete(product=product_id)

        response = JsonResponse({'product': product_id})
        # return redirect('cart_summary')
        messages.success(request, ("Item deleted from shopping cart."))
        return response


def cart_update(request: HttpRequest) -> JsonResponse:
    """
    Updates the quantity of a product in the cart and sends a success message.

    Args:
        request (HttpRequest): The HTTP request containing product details in POST data.

    Returns:
        JsonResponse: A JSON response containing the updated product quantity.
    """
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        # Get stuff
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))

        cart.update(product=product_id, quantity=product_qty)

        response = JsonResponse({'qty': product_qty})
        # return redirect('cart_summary')
        messages.success(request, ("Your cart has been updated."))
        return response

