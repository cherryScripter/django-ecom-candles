from django.db import models
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save


# Create Customer Profile
class Profile(models.Model):
    """
    Represents a user profile containing additional information not present
    in the default User model, such as address and contact details.
    Automatically created when a User is registered.

    Attributes:
        user (User): One-to-one relation with the User model.
        date_modified (datetime): Timestamp for the last modification.
        phone (str): User's phone number (optional).
        address1 (str): Primary address line (optional).
        address2 (str): Secondary address line (optional).
        city (str): User's city (optional).
        state (str): User's state (optional).
        zipcode (str): Postal code (optional).
        country (str): Country of residence (optional).
        old_cart (str): JSON-encoded representation of the user's previous cart (optional).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_modified = models.DateTimeField(auto_now=True)
    phone = models.CharField(max_length=20, blank=True)
    address1 = models.CharField(max_length=200, blank=True)
    address2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True)
    zipcode = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    old_cart = models.CharField(max_length=200, blank=True, null=True)

    @property
    def full_name(self) -> str:
        """
        Returns the full name of the user.

        Returns:
            str: Concatenated first and last name.
        """
        return f"{self.user.first_name} {self.user.last_name}".strip()

    def __str__(self)-> str:
        """
        Returns the string representation of the Profile.

        Returns:
            str: Username of the associated User.
        """
        return self.user.username


# Create a user Profile by default when user signs up
def create_profile(sender, instance, created, **kwargs):
    """
    Signal to create a Profile for a newly registered User.

    Args:
        sender (Model): The model class that triggered the signal.
        instance (User): The User instance being saved.
        created (bool): Whether a new User instance was created.
        **kwargs: Additional keyword arguments.
    """
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()


# Automate the profile thing
post_save.connect(create_profile, sender=User)


# Categories of Products
class Category(models.Model):
    """
    Represents a category of products.

    Attributes:
        name (str): Name of the category.
    """
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        """
        Returns the string representation of the Category.

        Returns:
            str: The category name.
        """
        return self.name

    class Meta:
        verbose_name_plural = 'categories'


# Customers
class Customer(models.Model):
    """
    Represents a customer with contact and login details.

    Attributes:
        first_name (str): Customer's first name.
        last_name (str): Customer's last name.
        phone (str): Customer's phone number.
        email (str): Customer's email (must be unique).
        password (str): Encrypted password for the customer.
    """
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=100)

    def __str__(self) -> str:
        """
        Returns the string representation of the Customer.

        Returns:
            str: Full name of the customer.
        """
        return f'{self.first_name} {self.last_name}'


# All of our Products
class Product(models.Model):
    """
    Represents product available in the store.

    Attributes:
        name (str): Name of the product.
        price (Decimal): Price of the product.
        category (Category): Category the product belongs to.
        description (str): Short description of the product (optional).
        image (ImageField): Image of the product.
        is_sale (bool): Indicates if the product is on sale.
        sale_price (Decimal): Discounted sale price (if applicable).
    """
    name = models.CharField(max_length=100)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=6)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    description = models.CharField(max_length=250, default='', blank=True, null=True)
    image = models.ImageField(
        upload_to='uploads/product/',
        default='https://djangoecomproject.s3.us-east-1.amazonaws.com/default.jpeg'),
    # Add Sale Stuff
    is_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(default=0, decimal_places=2, max_digits=6)

    def __str__(self) -> str:
        """
        Returns the string representation of the Product.

        Returns:
            str: Product name.
        """
        return self.name


class ProductReview(models.Model):
    """
    Represents a review for a specific product.

    Attributes:
        product (Product): The product being reviewed.
        user (User): The user who submitted the review.
        order_item (OrderItem): The order item associated with the review.
        content (str): Content of the review (optional).
        rating (int): Rating given to the product (out of 5).
        date (datetime): The date the review was submitted.
    """
    # from store.models import Order
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    order_item = models.OneToOneField('payment.OrderItem', on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField(blank=True, null=True, max_length=400)
    rating = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        """
        Returns the string representation of the ProductReview.

        Returns:
            str: Review summary including user, rating, and product.
        """
        return f"{self.user} - {self.rating}/5 for {self.product.name}"


# Customer Orders
class Order(models.Model):
    """
    Represents a customer order for a product.

    Attributes:
        product (Product): The product being ordered.
        customer (Customer): The customer placing the order.
        quantity (int): The quantity of the product ordered.
        address (str): The shipping address for the order.
        phone (str): The contact phone number for the order.
        date (datetime): The date the order was placed.
        status (bool): The status of the order (processed or not).

    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    address = models.CharField(max_length=100, default='', blank=True)
    phone = models.CharField(max_length=20, default='', blank=True)
    date = models.DateField(default=datetime.datetime.today, blank=True, null=True)
    status = models.BooleanField(default=False)

    def __str__(self) -> str:
        """
        Returns the string representation of the Order.

        Returns:
            str: The name of the ordered product.
        """
        return self.product
