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
from store.views import register, user_login, index, product_detail # Ensure you import the login view
from django.contrib.auth import views as auth_views  # Import for auth views

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin URL for Django's admin interface
    path('', index, name='index'),  # Home page mapped to the 'index' view
    path('register/', register, name='register'),  # Registration URL
    path('login/', user_login, name='login'),  # Add this line for login
    path('logout/', auth_views.LogoutView.as_view(template_name='store/logout.html'), name='logout'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
]
