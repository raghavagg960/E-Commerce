from django.urls import path
from .views import UserViewSet, AddressViewSet

user_list = UserViewSet.as_view({
    'post': 'register_user'
})

user_login = UserViewSet.as_view({
    'post': 'login_user'
})

urlpatterns = [
    path('register/', user_list, name='user-register'),
    path('login/', user_login, name='user-login'),
    
    # Address routes
    path('addresses/', AddressViewSet.as_view({'get': 'list', 'post': 'create'}), name='address-list'),
    path('addresses/<int:pk>/', AddressViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='address-detail'),
]

