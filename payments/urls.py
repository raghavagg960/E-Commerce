from django.urls import path
from .views import PaymentViewSet

urlpatterns = [
    path('', PaymentViewSet.as_view({'post': 'create'})),
]
