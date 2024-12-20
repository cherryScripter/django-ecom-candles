import datetime
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib import messages
from store.models import Product, Profile, ProductReview
from django.shortcuts import render
from .models import Order
# Import Some PayPal Stuff
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
# unique user id for duplictate orders
import uuid


def orders(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Admin view to manage and update the shipping status of a specific order.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the order to manage.

    Returns:
        HttpResponse: Renders the order details or redirects on failure.
    """
    if request.user.is_authenticated and request.user.is_superuser:
        # Get the order
        order = Order.objects.get(id=pk)
        # Get the order items
        items = OrderItem.objects.filter(order=pk)

        if request.POST:
            status = request.POST['shipping_status']
            # Check if true or false
            if status == "true":
                # Get the order
                order = Order.objects.filter(id=pk)
                # Update the status
                now = datetime.datetime.now()
                order.update(shipped=True, date_shipped=now)
            else:
                # Get the order
                order = Order.objects.filter(id=pk)
                # Update the status
                order.update(shipped=False)
            messages.success(request, "Shipping Status Updated")
            return redirect('home')

        return render(request, 'payment/orders.html', {"order": order, "items": items})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')


def not_shipped_dash(request: HttpRequest) -> HttpResponse:
    """
    Admin view to display orders that have not been shipped yet.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the dashboard of unshipped orders or redirects on failure.
    """
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            # Get the order
            order = Order.objects.filter(id=num)
            # grab Date and time
            now = datetime.datetime.now()
            # update order
            order.update(shipped=True, date_shipped=now)
            # redirect
            messages.success(request, "Shipping Status Updated")
            return redirect('home')

        return render(request, "payment/not_shipped_dash.html", {"orders": orders})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')


def shipped_dash(request: HttpRequest) -> HttpResponse:
    """
    Admin view to display orders that have been shipped.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the dashboard of shipped orders or redirects on failure.
    """
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            # grab the order
            order = Order.objects.filter(id=num)
            # grab Date and time
            now = datetime.datetime.now()
            # update order
            order.update(shipped=False)
            # redirect
            messages.success(request, "Shipping Status Updated")
            return redirect('home')
        return render(request, "payment/shipped_dash.html", {"orders": orders})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')


def process_order(request: HttpRequest) -> HttpResponse:
    """
    Processes an order from the cart, creates order and order items,
    and clears the cart upon completion.

    Args:
        request (HttpRequest): The HTTP request object containing order and session data.

    Returns:
        HttpResponse: Redirects to the home page with success or access-denied messages.
    """
    if request.POST:
        # Get the cart
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()

        # Get Billing Info from the last page
        payment_form = PaymentForm(request.POST or None)
        # Get Shipping Session Data
        my_shipping = request.session.get('my_shipping')

        # Gather Order Info
        full_name = my_shipping['full_name']
        email = my_shipping['shipping_email']
        # Create Shipping Address from session info
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
        amount_paid = totals

        # Create an Order
        if request.user.is_authenticated:
            # logged in
            user = request.user
            create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address,
                                 amount_paid=amount_paid)
            create_order.save()

            # Add order items

            # Get the order ID
            order_id = create_order.pk

            # Get product Info
            for product in cart_products():
                # Get product ID
                product_id = product.id
                # Get product price
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price

                    # Get quantity
                for key, value in quantities().items():
                    if int(key) == product.id:
                        # Create order item
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, user=user,
                                                      quantity=value,
                                                      price=price)
                        create_order_item.save()

                # Delete the cart
                for key in list(request.session.keys()):
                    if key == "session_key":
                        # Delete the key
                        del request.session[key]

                # Delete Cart from Database (old_cart field)
                current_user = Profile.objects.filter(user__id=request.user.id)
                # Delete shopping cart in database (old_cart field)
                current_user.update(old_cart="")

            messages.success(request, 'Order placed.')
            return redirect('home')

        else:
            # not logged in
            # Create Order
            create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address,
                                 amount_paid=amount_paid)
            create_order.save()

            # Add order items

            # Get the order ID
            order_id = create_order.pk

            # Get product Info
            for product in cart_products():
                # Get product ID
                product_id = product.id
                # Get product price
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price

                    # Get quantity
                for key, value in quantities().items():
                    if int(key) == product.id:
                        # Create order item
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value,
                                                      price=price)
                        create_order_item.save()

            # Delete our cart
            for key in list(request.session.keys()):
                if key == "session_key":
                    # Delete the key
                    del request.session[key]

            messages.success(request, 'Order placed.')
            return redirect('home')

    else:
        messages.success(request, 'Access denied.')
        return redirect('home')


def billing_info(request: HttpRequest) -> HttpResponse:
    """
    Processes billing information and prepares PayPal payment data.

    Args:
        request (HttpRequest): The HTTP request object containing POST data for billing.

    Returns:
        HttpResponse: Renders the billing information page with PayPal form or redirects.
    """
    if request.POST:
        # Get the cart
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()

        # Create a session with Shipping Info
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping

        # Gather Order Info
        full_name = my_shipping['full_name']
        email = my_shipping['shipping_email']
        # Create Shipping Address from session info
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
        amount_paid = totals

        # Get the host
        host = request.get_host()
        # Create invoice number
        my_invoice = str(uuid.uuid4())

        # Create Paypal Form Dictionary
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': totals,
            'item_name': cart_products,
            'no_shipping': '2',
            'invoice': my_invoice,
            'currency_code': 'USD',  # EUR for Euros
            'notify_url': 'https://{}{}'.format(host, reverse("paypal-ipn")),
            'return_url': 'https://{}{}'.format(host, reverse("payment_success")),
            'cancel_return': 'https://{}{}'.format(host, reverse("payment_failed")),
        }

        # Create actual paypal button
        paypal_form = PayPalPaymentsForm(initial=paypal_dict)

        # Check to see if user is logged in
        if request.user.is_authenticated:
            # Get The Billing Form
            billing_form = PaymentForm()

            # logged in
            user = request.user
            create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address,
                                 amount_paid=amount_paid, invoice=my_invoice)
            create_order.save()

            # Add order items

            # Get the order ID
            order_id = create_order.pk

            # Get product Info
            for product in cart_products():
                # Get product ID
                product_id = product.id
                # Get product price
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price

                    # Get quantity
                for key, value in quantities().items():
                    if int(key) == product.id:
                        # Create order item
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, user=user,
                                                      quantity=value,
                                                      price=price)
                        create_order_item.save()

                # Delete Cart from Database (old_cart field)
                current_user = Profile.objects.filter(user__id=request.user.id)
                # Delete shopping cart in database (old_cart field)
                current_user.update(old_cart="")

            return render(request, "payment/billing_info.html",
                          {"paypal_form": paypal_form, "cart_products": cart_products, "quantities": quantities,
                           "totals": totals, "shipping_info": request.POST, "billing_form": billing_form})

        else:
            # not logged in
            # Create Order
            create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address,
                                 amount_paid=amount_paid, invoice=my_invoice)
            create_order.save()

            # Add order items

            # Get the order ID
            order_id = create_order.pk

            # Get product Info
            for product in cart_products():
                # Get product ID
                product_id = product.id
                # Get product price
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price

                    # Get quantity
                for key, value in quantities().items():
                    if int(key) == product.id:
                        # Create order item
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value,
                                                      price=price)
                        create_order_item.save()

            # Not logged in
            # Get The Billing Form
            billing_form = PaymentForm()
            return render(request, "payment/billing_info.html",
                          {"paypal_form": paypal_form, "cart_products": cart_products, "quantities": quantities,
                           "totals": totals, "shipping_info": request.POST, "billing_form": billing_form})

    else:
        messages.success(request, "Access Denied")
        return redirect('home')


def checkout(request: HttpRequest) -> HttpResponse:
    """
    Handles the checkout process for both authenticated users and guests.

    Args:
        request (HttpRequest): The HTTP request object containing cart and user information.

    Returns:
        HttpResponse: Renders the checkout page with shipping form and cart details.
    """
    # Get the cart
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()

    if request.user.is_authenticated:
        # Checkout as logged-in user
        # Shipping User
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        # Shipping Form
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        return render(request, "payment/checkout.html",
                      {"cart_products": cart_products, "quantities": quantities, "totals": totals,
                       "shipping_form": shipping_form})
    else:
        # Checkout as guest
        shipping_form = ShippingForm(request.POST or None)
        return render(request, "payment/checkout.html",
                      {"cart_products": cart_products, "quantities": quantities, "totals": totals,
                       "shipping_form": shipping_form})


def payment_success(request: HttpRequest) -> HttpResponse:
    """
    Handles the payment success process by clearing the cart and displaying a success page.

    Args:
        request (HttpRequest): The HTTP request object containing session and cart information.

    Returns:
        HttpResponse: Renders the payment success page.
    """
    # Delete items in the browser cart
    # Get the cart
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()

    # Delete the cart
    for key in list(request.session.keys()):
        if key == "session_key":
            # Delete the key
            del request.session[key]

    return render(request, 'payment/payment_success.html', {})


def payment_failed(request: HttpRequest) -> HttpResponse:
    """
    Handles the payment failure process by displaying an error message to the user.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the payment failure page with an appropriate message.
    """
    return render(request, 'payment/payment_failed.html', {})


def order_history(request):
    """
    Displays the order history table for authenticated users, including a review status for each item.
    Only shows orders that are marked as PAID.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the order history page with detailed order and review information.
    """
    user_orders = []  # Initialize list of orders with their items and review status

    if request.user.is_authenticated:
        # Fetch all paid orders associated with the user
        orders = Order.objects.filter(user=request.user, paid=True).order_by('-id')

        for order in orders:
            order_items = []

            for item in order.orderitem_set.all():
                # Check if the product has a review by the user
                has_review = item.product.reviews.filter(user=request.user).exists()
                order_items.append({
                    'item': item,
                    'has_review': has_review  # True if review exists, False otherwise
                })

            user_orders.append({'order': order, 'items': order_items})

    return render(request, 'payment/order_history.html', {
        'user_orders': user_orders
    })
