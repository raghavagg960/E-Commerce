from django.contrib import admin
from .models import Cart, CartItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user']

@admin.register(CartItem)
class CartAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity']
