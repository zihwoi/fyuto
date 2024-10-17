"""
URL configuration for fyuto project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from store import views
from store.views import register, user_login, index, product_detail, product_list, cart_detail, cart_add, cart_remove, checkout, checkout_success, checkout_error    # Ensure you import the login view
from django.contrib.auth import views as auth_views  # Import for auth views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),  # Admin URL for Django's admin interface
    path('', index, name='index'),  # Home page mapped to the 'index' view
    path('register/', register, name='register'),  # Registration URL
    path('login/', user_login, name='login'),  # Add this line for login
    path('logout/', auth_views.LogoutView.as_view(template_name='store/logout.html'), name='logout'),

    #Product related links
    path('products/', product_list, name='product_list'), 
    path('category/<int:category_id>/', views.product_list, name='product_list_by_category'), 
    path('product/<int:product_id>/', product_detail, name='product_detail'),

    # Cart-related URLs
    path('cart/', cart_detail, name='cart_detail'),  # View the cart
    path('cart/add/<int:product_id>/', cart_add, name='cart_add'),  # Add product to the cart
    path('cart/remove/<int:product_id>/', cart_remove, name='cart_remove'),  # Remove product from the cart

    # Checkout URL
    path('checkout/', checkout, name='checkout'),  # Checkout process
    path('checkout_success/', checkout_success, name='checkout_success'), #Checkout success page
    path('checkout_error/', checkout_error, name='checkout_error'), #error page
]

# For serving media files during development
if settings.DEBUG:  # Ensures this only runs in development mode
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)