from django.contrib import admin
from .models import Product, Category, Brand, ProductImage, Review

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'brand', 'price', 'stock', 'is_active']

    class Meta:
        model = Product

@admin.register(Category)    
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']

    class Meta:
        model = Category

@admin.register(Brand)    
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']

    class Meta:
        model = Brand

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image', 'is_main']

    class Meta:
        model = ProductImage

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'comment']

    class Meta:
        model = Review

