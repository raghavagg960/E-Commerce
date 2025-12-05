from django.urls import path
from .views import UserViewSet

user_list = UserViewSet.as_view({
    'post': 'register_user'
})

user_login = UserViewSet.as_view({
    'post': 'login_user'
})

urlpatterns = [
    path('register/', user_list, name='user-register'),
    path('login/', user_login, name='user-login'),
]

