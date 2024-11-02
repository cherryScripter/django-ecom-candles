from django.template.loader import render_to_string
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail, EmailMultiAlternatives
from .models import Order
from django.conf import settings


def send_payment_confirmation_email(order):
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


# def send_payment_confirmation_email(order):
#     subject = 'Payment Confirmation'
#     message = f'Thank you for your payment, {order.full_name}!\n\n' \
#               f'Your order (ID: {order.id}) has been confirmed.\n\n' \
#               f'We will ship it to the following address:\n' \
#               f'{order.shipping_address}\n\n' \
#               'We appreciate your business!'
#
#     from_email = settings.EMAIL_HOST_USER
#     recipient_list = [order.email]
#
#     send_mail(subject, message, from_email, recipient_list)


@receiver(post_save, sender=Order)
def order_paid(sender, instance, created, **kwargs):
    # Only send the email if the order is updated and marked as paid
    if not created and instance.paid:
        send_payment_confirmation_email(instance)
