from django.shortcuts import render, get_object_or_404
from .cart import Cart
from django.apps import apps
# from store.models import Product
from django.http import JsonResponse
from django.contrib import messages

model_product = apps.get_model('store', 'Product')


def cart_summary(request):
    # Get the cart
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()
    return render(request, 'cart_summary.html',
                  {"cart_products": cart_products, "quantities": quantities, "totals": totals})


def cart_add(request):
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
# def cart_add(request):
#     # Get the cart
#     cart = Cart(request)
#     # test for POST
#     if request.POST.get('action') == 'post':
#         # Get stuff
#         product_id = int(request.POST.get('product_id'))
#         product_qty = int(request.POST.get('product_qty'))
#
#         # lookup product in DB
#         product = get_object_or_404(model_product, id=product_id)
#
#         # Try adding the product to the cart
#         if not cart.add(product=product, quantity=product_qty):
#             # Max quantity exceeded, show error message
#             messages.error(request, "Maximum quantity for this product has been reached.")
#             return JsonResponse({'error': "Max quantity exceeded"})
#
#         # Get Cart Quantity
#         cart_quantity = cart.__len__()
#
#         # Send success response
#         response = JsonResponse({'qty': cart_quantity})
#         messages.success(request, "Product added to the cart.")
#         return response
#




        # # Save to session
        # cart.add(product=product, quantity=product_qty)
        #
        # # Get Cart Quantity
        # cart_quantity = cart.__len__()
        #
        # # Return resonse
        # # response = JsonResponse({'Product Name: ': product.name})
        # response = JsonResponse({'qty': cart_quantity})
        # messages.success(request, ("Product added to a cart."))
        # return response


def cart_delete(request):
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


def cart_update(request):
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

