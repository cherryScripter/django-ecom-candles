from django.template.loader import render_to_string
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail, EmailMultiAlternatives
from .models import Order
from django.conf import settings


def send_payment_confirmation_email(order):
    """
    Sends a payment confirmation email to the customer after an order is marked as paid.

    Args:
        order (Order): The order object containing payment and customer details.

    Returns:
        None
    """
    # Email subject
    subject = f'Payment Confirmation - Order ID: {order.id}'

    # Prepare context for the template
    order_items = order.orderitem_set.all()  # Fetch associated OrderItems
    total_amount = order.amount_paid  # Total amount paid

    # Prepare formatted list of items purchased
    items_list = []
    for item in order_items:
        items_list.append(f'{item.product.name} (Quantity: {item.quantity}) - ${item.price:.2f}')

    # Render the email body using the HTML template
    context = {
        'name': order.full_name,
        'cart_products': items_list,  # Pass the formatted list
        'totals': total_amount,
    }

    # Render the HTML message using the template
    html_message = render_to_string('payment/email_template.html', context)

    from_email = settings.EMAIL_HOST_USER
    recipient_list = [order.email]

    # Create the email message
    email = EmailMultiAlternatives(subject, '', from_email, recipient_list)
    email.attach_alternative(html_message, "text/html")

    # Send the email
    email.send(fail_silently=False)


@receiver(post_save, sender=Order)
def order_paid(sender, instance, created, **kwargs):
    """
    Signal receiver triggered when an Order is saved. Sends a payment confirmation email if the order is marked as paid.

    Args:
        sender (type): The model class that sent the signal (Order).
        instance (Order): The instance of the model being saved.
        created (bool): Indicates if this is a new instance being created.
        kwargs: Additional keyword arguments.

    Returns:
        None
    """
    # Only send the email if the order is updated and marked as paid
    if not created and instance.paid:
        send_payment_confirmation_email(instance)
