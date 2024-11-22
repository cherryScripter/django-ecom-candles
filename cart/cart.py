# from store.models import Product, Profile
from django.conf import settings
from django.apps import apps

model_product = apps.get_model('store', 'Product')
model_profile = apps.get_model('store', 'Profile')


class Cart:
    """
    Represents a shopping cart. Supports adding, updating, deleting products,
    and handling user-specific cart persistence.
    """
    def __init__(self, request):
        """
        Initialize the cart with the current session data.

        Args:
            request (HttpRequest): The HTTP request containing session and user information.
        """
        self.session = request.session
        # Get request
        self.request = request
        # Get the current session key if it exists
        cart = self.session.get('session_key')

        # If the user is new, no session key!  Create one!
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        # Make sure cart is available on all pages of site
        self.cart = cart

    def db_add(self, product: int, quantity: int) -> None:
        """
        Adds a product to the database-backed cart.

        Args:
            product (int): Product ID.
            quantity (int): Quantity of the product to add.
        """
        product_id = str(product)
        product_qty = str(quantity)
        # Logic
        if product_id in self.cart:
            pass
        else:
            # self.cart[product_id] = {'price': str(product.price)}
            self.cart[product_id] = int(product_qty)

        self.session.modified = True

        # Deal with logged in user
        if self.request.user.is_authenticated:
            # Get the current user profile
            current_user = model_profile.objects.filter(user__id=self.request.user.id)
            # Convert {'3':1, '2':4} to {"3":1, "2":4}
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            # Save carty to the Profile Model
            current_user.update(old_cart=str(carty))

    def add(self, product: Product, quantity: int) -> bool:
        """
        Adds or updates a product in the cart, respecting a maximum quantity limit.

        Args:
            product (Product): The product object.
            quantity (int): Quantity to add.

        Returns:
            bool: True if the product was added, False if the maximum quantity was exceeded.
        """
        product_id = str(product.id)

        # Set the maximum quantity limit here
        max_quantity = 7

        # Get the current quantity of the product in the cart (if it exists), otherwise 0
        current_quantity = self.cart.get(product_id, 0)

        # Calculate the new quantity by adding the new quantity to the current quantity
        new_quantity = current_quantity + quantity

        # Check if the new quantity exceeds the max limit
        if new_quantity > max_quantity:
            return False  # Indicate that adding the product exceeds the limit

        # Add the product to the cart or update its quantity
        self.cart[product_id] = new_quantity

        # Mark the session as modified to ensure it is saved
        self.session.modified = True

        # Save the cart to the user's profile if the user is authenticated
        if self.request.user.is_authenticated:
            current_user = model_profile.objects.filter(user__id=self.request.user.id)
            carty = str(self.cart).replace("\'", "\"")  # Convert cart dict to JSON-like format
            current_user.update(old_cart=str(carty))
        return True

    def cart_total(self) -> float:
        """
        Calculates the total cost of the cart.

        Returns:
            float: The total price of all items in the cart.
        """
        # Get product IDS
        product_ids = self.cart.keys()
        # lookup those keys in our products database model
        products = model_product.objects.filter(id__in=product_ids)
        # Get quantities
        quantities = self.cart
        # Start counting at 0
        total = 0

        for key, value in quantities.items():
            # Convert key string into int so we can do math
            key = int(key)
            # Ensure value (quantity) is an integer
            quantity = int(value)
            for product in products:
                if product.id == key:
                    if product.is_sale:
                        # Multiply Decimal price by integer quantity
                        total = total + (product.sale_price * quantity)
                    else:
                        # Multiply Decimal price by integer quantity
                        total = total + (product.price * quantity)

        return total

    def __len__(self) -> float:
        """
        Returns the number of unique items in the cart.

        Returns:
            int: Number of items in the cart.
        """
        return len(self.cart)

    def get_prods(self):
        """
        Retrieves product objects corresponding to items in the cart.

        Returns:
            QuerySet: A Django QuerySet of products.
        """
        # Get ids from cart
        product_ids = self.cart.keys()
        # Use ids to lookup products in database model
        products = model_product.objects.filter(id__in=product_ids)

        # Return those looked up products
        return products

    def get_quants(self) -> dict:
        """
         Returns the quantities of each product in the cart.

         Returns:
             dict: A dictionary mapping product IDs to their quantities.
         """
        quantities = self.cart
        return quantities

    def update(self, product: int, quantity: int) -> dict:
        """
        Updates the quantity of a product in the cart.

        Args:
            product (int): Product ID.
            quantity (int): New quantity.

        Returns:
            dict: Updated cart dictionary.
        """
        product_id = str(product)
        product_qty = int(quantity)

        # Get cart
        ourcart = self.cart
        # Update Dictionary/cart
        ourcart[product_id] = product_qty

        self.session.modified = True

        # Deal with logged in user
        if self.request.user.is_authenticated:
            # Get the current user profile
            current_user = model_profile.objects.filter(user__id=self.request.user.id)
            # Convert {'3':1, '2':4} to {"3":1, "2":4}
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            # Save carty to the Profile Model
            current_user.update(old_cart=str(carty))

        thing = self.cart
        return thing

    def delete(self, product: int) -> None:
        """
        Removes a product from the cart.

        Args:
            product (int): Product ID.
        """
        product_id = str(product)
        # Delete from dictionary/cart
        if product_id in self.cart:
            del self.cart[product_id]

        self.session.modified = True

        # Deal with logged in user
        if self.request.user.is_authenticated:
            # Get the current user profile
            current_user = model_profile.objects.filter(user__id=self.request.user.id)
            # Convert {'3':1, '2':4} to {"3":1, "2":4}
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            # Save carty to the Profile Model
            current_user.update(old_cart=str(carty))
