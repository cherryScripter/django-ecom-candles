from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Order
from django.conf import settings


@receiver(post_save, sender=Order)
def order_paid(sender, instance, created, **kwargs):
    # Only send an email if the order was updated and is now marked as paid
    if not created and instance.paid:
        send_payment_confirmation_email(instance.email)


def send_payment_confirmation_email(email):
    subject = 'Payment Confirmation'
    message = 'Thank you for your payment! Your order has been confirmed.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list)




   #### TEMPLATE EMAIL ??
    #
    # # Extract shipping info from the form submission
    # my_shipping = request.POST
    # full_name = my_shipping['shipping_full_name']
    # email_customer = my_shipping['shipping_email']
    # print(full_name)
    # print(email_customer)
    #
    # # Create a context dictionary for the email template
    # context = {
    #     'name': full_name,
    #     'cart_products': cart_products,
    #     'totals': totals,
    #     'quantities': quantities
    # }
    #
    # # Render the email template with context
    # template = render_to_string('payment/email_template.html', context)
    #
    # # Create the email
    # email = EmailMessage(
    #     'Order Confirmation - Thank You for Your Purchase!',
    #     template,
    #     settings.EMAIL_HOST_USER,
    #     [email_customer]
    # )
    # email.fail_silently = False
    #
