from django.urls import path
from .views import OrderViewSet

order_create = OrderViewSet.as_view({'post': 'create'})
order_my = OrderViewSet.as_view({'get': 'my_orders'})
order_vendor = OrderViewSet.as_view({'get': 'vendor_orders'})

urlpatterns = [
    path('', order_create),        # POST /orders/
    path('my/', order_my),         # GET  /orders/my/
    path('vendor/', order_vendor)  # GET  /orders/vendor/
]
