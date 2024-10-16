from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category  # Import Product and Category

# Register Product model
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category', 'image_preview')  # Add image_preview to list_display

    # Custom method to display the product image
    def image_preview(self, obj):
        if obj.image:  # Check if the product has an image
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return 'No Image'

    image_preview.short_description = 'Image Preview'  # Set column name in admin

# Register Category model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Display category name
