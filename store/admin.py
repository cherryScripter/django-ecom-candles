from django.contrib import admin
from .models import Category, Customer, Product, Order, Profile, ProductReview
from django.contrib.auth.models import User

admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Profile)
admin.site.register(ProductReview)


# Mix Profile info and User info
class ProfileInline(admin.StackedInline):
    """
    Allows the Profile model to be edited inline within the User admin page.

    This enables editing additional user profile information without navigating to a separate page.
    """
    model = Profile


# Extend User model
class UserAdmin(admin.ModelAdmin):
    """
    Customizes the User admin interface by extending the default User model.

    Fields:
        - username: The user's login name.
        - first_name: The user's first name.
        - last_name: The user's last name.
        - email: The user's email address.

    Inline:
        - ProfileInline: Includes Profile fields within the User admin page.
    """
    model = User
    field = ["username", "first_name", "last_name", "email"]
    inlines = [ProfileInline]


# Unregister the old way
admin.site.unregister(User)

# Re-Register the new way
admin.site.register(User, UserAdmin)
