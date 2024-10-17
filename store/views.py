# Create your views here.
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .models import Product, Category
from .cart import Cart
import stripe
from django.conf import settings  # Import the settings module

stripe.api_key = settings.STRIPE_SECRET_KEY  # Use the secret key from settings

def index(request):
    products = Product.objects.all()
    return render(request, 'store/index.html', {'products': products})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.success(request, 'Registration successful! You are now logged in.')
            return redirect('store:index')
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = UserCreationForm()
    return render(request, 'store/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
        if user is not None:
                login(request, user)
                return redirect('store:index')  # Adjust this redirect as needed
    else:
        form = AuthenticationForm()

    return render(request, 'store/login.html', {'form': form})  # Ensure you have a login.html

def product_list(request, category_id=None):
    categories = Category.objects.all()
    products = Product.objects.all()

    if category_id:
        products = products.filter(category_id=category_id)
    
    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'store/product_list.html', context)

    # store/views.py

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    context = {
        'product': product
    }
    return render(request, 'store/product_detail.html', context)

def cart_add(request, product_id):
    """Add product to the cart."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product)
    return redirect('cart_detail')

def cart_remove(request, product_id):
    """Remove product from the cart."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')

def cart_detail(request):
    """View for displaying the cart's contents."""
    cart = Cart(request)
    return render(request, 'store/cart_detail.html', {'cart': cart})

def checkout(request):
    cart = Cart(request)
    total = int(cart.get_total_price() * 100)  # Convert to cents for Stripe

    if request.method == 'POST':
        stripe_token = request.POST.get('stripeToken')

        if not stripe_token:
            messages.error(request, 'Stripe token is missing. Please try again.')
            return redirect('cart_detail')

        try:
            charge = stripe.Charge.create(
                amount=total,  # Amount in cents
                currency='usd',
                description='Order payment',
                source=stripe_token
            )
            # Clear cart after successful payment
            cart.clear()
            return render(request, 'store/checkout_success.html')
        except stripe.error.StripeError as e:
            messages.error(request, 'Payment error: {}'.format(e.user_message))
            return render(request, 'store/checkout_error.html')

    return render(request, 'store/checkout.html', {
        'cart': cart,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })


def checkout_success(request):
    return render(request, 'store/checkout_success.html')

def checkout_error(request):
    return render(request, 'store/checkout_error.html')