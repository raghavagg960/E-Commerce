from django.urls import path
from .views import CartViewSet

cart_list = CartViewSet.as_view({'get': 'list'})
cart_add = CartViewSet.as_view({'post': 'add'})
cart_item_update = CartViewSet.as_view({'put': 'update_item'})
cart_item_delete = CartViewSet.as_view({'delete': 'remove_item'})

urlpatterns = [
    path('', cart_list),
    path('add/', cart_add),
    path('item/<int:pk>/', cart_item_update),
    path('item/<int:pk>/delete/', cart_item_delete),
]