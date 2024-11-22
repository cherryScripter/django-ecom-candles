from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import datetime


class ShippingAddress(models.Model):
    """
        Represents the shipping address of a user.

        Attributes:
            user (ForeignKey): The user associated with the shipping address.
            full_name (str): The full name of the person receiving the shipment.
            shipping_email (str): The email address associated with the shipping address.
            shipping_address1 (str): The primary address line.
            shipping_address2 (str): The secondary address line (optional).
            shipping_city (str): The city where the shipment will be delivered.
            shipping_state (str): The state/province (optional).
            shipping_zipcode (str): The postal code for the address (optional).
            shipping_country (str): The country where the shipment will be delivered.
        """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    shipping_email = models.CharField(max_length=255)
    shipping_address1 = models.CharField(max_length=255)
    shipping_address2 = models.CharField(max_length=255, null=True, blank=True)
    shipping_city = models.CharField(max_length=255)
    shipping_state = models.CharField(max_length=255, null=True, blank=True)
    shipping_zipcode = models.CharField(max_length=255, null=True, blank=True)
    shipping_country = models.CharField(max_length=255)

    # Don't pluralize address
    class Meta:
        verbose_name_plural = "Shipping Address"

    def __str__(self):
        return f'Shipping Address - {str(self.id)}'


# Create a user Shipping Address by default when user signs up
def create_shipping(sender, instance, created, **kwargs):
    """
    Automatically creates a ShippingAddress instance for a new user.
    """
    if created:
        user_shipping = ShippingAddress(user=instance)
        user_shipping.save()


# Automate the profile thing
post_save.connect(create_shipping, sender=User)


# Create Order Model
class Order(models.Model):
    """
    Represents an order placed by a user, including shipping and payment details.

    Attributes:
        user (ForeignKey): The user who placed the order.
        full_name (str): Full name of the person placing the order.
        email (str): The email address for order correspondence.
        shipping_address (ForeignKey): The shipping address for the order.
        amount_paid (Decimal): The total amount paid for the order.
        date_ordered (DateTime): The date and time when the order was placed.
        shipped (bool): Whether the order has been shipped.
        date_shipped (DateTime): The date and time when the order was shipped (nullable).
        invoice (str): The invoice identifier (nullable).
        paid (bool): Whether the order has been paid.
    """
    # Foreign Key
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_orders', null=True, blank=True)
    full_name = models.CharField(max_length=250)
    email = models.EmailField(max_length=250)
    shipping_address = models.TextField(max_length=15000)
    amount_paid = models.DecimalField(max_digits=7, decimal_places=2)
    date_ordered = models.DateTimeField(auto_now_add=True)
    shipped = models.BooleanField(default=False)
    date_shipped = models.DateTimeField(blank=True, null=True)
    # Paypal Invoice and Paid T/F
    invoice = models.CharField(max_length=250, blank=True, null=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f'Order - {str(self.id)}'


# Auto Add shipping Date
@receiver(pre_save, sender=Order)
def set_shipped_date_on_update(sender, instance, **kwargs):
    """
    Automatically sets the `date_shipped` field when the order is marked as shipped.
    """
    if instance.pk:
        now = datetime.datetime.now()
        obj = sender._default_manager.get(pk=instance.pk)
        if instance.shipped and not obj.shipped:
            instance.date_shipped = now


# Create Order Items Model
class OrderItem(models.Model):
    """
    Represents an individual item within an order.

    Attributes:
        order (ForeignKey): The order that this item belongs to.
        product (ForeignKey): The product being purchased.
        user (ForeignKey): User who purchased the item (optional).
        quantity (PositiveBigIntegerField): Quantity of the product in the order.
        price (DecimalField): Price of the product at the time of purchase.
    """
    from store.models import Product
    # Foreign Keys
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(max_digits=7, decimal_places=2)


    def __str__(self):
        return f'Order Item - {str(self.id)}'
