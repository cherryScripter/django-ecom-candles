from django.http import JsonResponse
from django.shortcuts import render, redirect
import requests
from .models import Product, Category, Profile, ProductReview
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django import forms
from django.db.models import Q
import json
from cart.cart import Cart
from payment.models import OrderItem



def search(request):
    # Determine if they filled out the form
    if request.method == "POST":
        searched = request.POST['searched']
        # Query The Products DB Model
        searched = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched))
        # Test for null
        if not searched:
            messages.success(request, "That product does not exist. Please try again.")
            return render(request, "search.html", {})
        else:
            return render(request, "search.html", {'searched': searched})
    else:
        return render(request, "search.html", {})


def update_info(request):
    if request.user.is_authenticated:
        # Get Current User
        current_user = Profile.objects.get(user__id=request.user.id)
        # Get Current User's Shipping Info
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)

        # Get original User Form
        form = UserInfoForm(request.POST or None, instance=current_user)
        # Get User's Shipping Form
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        if form.is_valid() or shipping_form.is_valid():
            # Save original form
            form.save()
            # Save shipping form
            shipping_form.save()

            messages.success(request, "Your info has been updated.")
            return redirect('home')
        return render(request, "update_info.html", {'form': form, 'shipping_form': shipping_form})
    else:
        messages.success(request, "You must be logged in to access that page.")
        return redirect('home')


def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        # Did they fill out the form
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            # Is the form valid
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been updated.")
                login(request, current_user)
                return redirect('update_user')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')
        else:
            form = ChangePasswordForm(current_user)
            return render(request, "update_password.html", {'form': form})
    else:
        messages.success(request, "You must be logged in to access that page.")
        return redirect('home')


def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)

        if user_form.is_valid():
            user_form.save()

            login(request, current_user)
            messages.success(request, "User has been updated.")
            return redirect('home')

        return render(request, "update_user.html", {'user_form': user_form})
    else:
        messages.success(request, "You must be logged in to access that page.")
        return redirect('home')


def category_summary(request):
    categories = Category.objects.all()
    return render(request, 'category_summary.html', {"categories": categories})


def category(request, foo):
    # Replace Hyphens with Spaces
    foo = foo.replace('-', ' ')
    # Grab the category from the url
    try:
        # Look Up The Category
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products': products, 'category': category})
    except:
        messages.success(request, "That category doesn't exist.")
        return redirect('home')

#
# def product(request, pk):
#     product = Product.objects.get(id=pk)
#     reviews = ProductReview.objects.filter(product=product)
#     # Prepare stars for each review
#     for review in reviews:
#         review.stars = '⭐' * review.rating
#
#     # Add a review
#     if request.method == "POST" and request.user.is_authenticated:
#         rating = request.POST.get('rating', 3)
#         content = request.POST.get('content', '')
#
#         review = ProductReview.objects.create(product=product, user=request.user, rating=rating, content=content)
#
#         return redirect('product', pk=product.id)
#
#     return render(request, 'product.html', {'product': product, 'reviews': reviews})


def product(request, pk):
    product = Product.objects.get(id=pk)
    reviews = ProductReview.objects.filter(product=product)

    # Display stars for each review rating
    for review in reviews:
        review.stars = '⭐' * review.rating

    # Initialize message variable
    review_message = ""

    if request.user.is_authenticated:
        # Check if the user has purchased this product
        order_item = OrderItem.objects.filter(
            product=product,
            user=request.user,
            order__paid=True
        ).first()

        if order_item:
            # Check if the user has already reviewed this product
            if ProductReview.objects.filter(product=product, user=request.user).exists():
                review_message = "You have already added your review."
            else:
                # Allow review submission
                if request.method == "POST":
                    rating = request.POST.get('rating', 3)
                    content = request.POST.get('content', '')
                    ProductReview.objects.create(
                        product=product,
                        user=request.user,
                        rating=rating,
                        content=content
                    )
                    messages.success(request, "Thank you! Your review has been successfully submitted.")
                    return redirect('product', pk=product.id)
        else:
            review_message = "You have to purchase this product first to add a review."

    return render(request, 'product.html', {
        'product': product,
        'reviews': reviews,
        'review_message': review_message,  # Pass the message to the template
    })







# def home(request):
#     products = Product.objects.all()
#     return render(request, 'home.html', {'products': products})
#
#

def home(request):
    products = Product.objects.all()

    # Check for the sort_by parameter in the GET request
    sort_by = request.GET.get('sort_by')
    if sort_by == 'price_asc':
        products = products.order_by('price')  # Sort by price ascending
    elif sort_by == 'price_desc':
        products = products.order_by('-price')  # Sort by price descending

    return render(request, 'home.html', {'products': products})



def about(request):
    return render(request, 'about.html', {})


def get_inspired(request):
    api_url = 'https://zenquotes.io/api/random'

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        api_data = response.json()

        # Extracting the quote and author from the JSON data
        quote = api_data[0]['q']  # Accessing the quote text
        author = api_data[0]['a']  # Accessing the author's name

        # Check if the request is made via AJAX by checking the headers
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'quote': quote, 'author': author})

    except requests.exceptions.RequestException as e:
        quote = None  # If there's an error, set quote to None
        author = None  # If there's an error, set author to None
        print(f"An error occurred: {e}")

    return render(request, 'get_inspired.html', {'quote': quote, 'author': author})


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Do some shopping cart stuff
            current_user = Profile.objects.get(user__id=request.user.id)
            # Get their saved cart from database
            saved_cart = current_user.old_cart
            # Convert database string to python dictionary
            if saved_cart:
                # Convert to dictionary using JSON
                converted_cart = json.loads(saved_cart)
                # Add the loaded cart dictionary to our session
                # Get the cart
                cart = Cart(request)
                # Loop through the cart and add the items from the database
                for key, value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)

            messages.success(request, "You have been logged in!")

            # Get the 'next' parameter from the request
            next_url = request.POST.get('next') or 'home'  # Redirect to 'home' if next is not provided
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Please try again.")
            return redirect('login')

    else:
        next_url = request.GET.get('next', '')  # Capture the next parameter for GET requests
        return render(request, 'login.html', {'next': next_url})


def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')


def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # log in user
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "Username created - Please fill out your user info below.")
            return redirect('update_info')
        else:
            messages.success(request, "Whoops! There was a problem registering, please try again.")
            return redirect('register')
    else:
        return render(request, 'register.html', {'form': form})


def password_reset(request):
    return render(request, 'password_reset.html', {})
