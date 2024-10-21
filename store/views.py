# Create your views here.
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .models import Product, Category
from .cart import Cart
import stripe, logging
from django.conf import settings  # Import the settings module
from django.http import JsonResponse

# Set up logger
logger = logging.getLogger(__name__)

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
            messages.success(request, 'Registration successful! Please login with your credentials.')
            return redirect('login')  # Redirect to login page after successful registration
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
                messages.success(request, f'Welcome back, {username}!')
                return redirect('index')  # Redirect to home page after successful login
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'store/login.html', {'form': form})

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
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    # Get quantity from POST request and convert it to integer
    quantity = request.POST.get('quantity', 1)  # Default to 1 if not provided
    quantity = int(quantity)  # Ensure quantity is an integer
    
    # Add the product to the cart with the specified quantity
    cart.add(product, quantity)

     # Return JSON response for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'Product added to cart successfully'
        })
    
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

    # Check if cart is empty
    if len(cart) == 0:
        messages.error(request, 'Your cart is empty. Please add items before proceeding to checkout.')
        return redirect('cart_detail')

    # Process the form submission (POST)
    if request.method == 'POST':
        stripe_token = request.POST.get('stripeToken')

        # Ensure Stripe token is present
        if not stripe_token:
            messages.error(request, 'Stripe token is missing. Please try again.')
            return redirect('cart_detail')

        try:
            # Create a Stripe charge
            charge = stripe.Charge.create(
                amount=total,  # Amount in cents
                currency='usd',
                description='Order payment',
                source=stripe_token
            )
            
            # Log successful charge
            logger.info(f'Charge successful: {charge.id}')

            # Clear the cart after a successful charge
            cart.clear()

            # Redirect to success page
            return redirect('checkout_success')

        except stripe.error.StripeError as e:
            # Log and display the error message
            logger.error(f'Error during payment: {e}')
            messages.error(request, f'Payment error: {e.user_message}')
            return render(request, 'store/checkout_error.html')

    # If GET request, render checkout page with the Stripe public key
    return render(request, 'store/checkout.html', {
        'cart': cart,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY  # Pass public key to frontend
    })

def checkout_success(request):
    return render(request, 'store/checkout_success.html')

def checkout_error(request):
    return render(request, 'store/checkout_error.html')