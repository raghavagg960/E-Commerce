from django.shortcuts import render
from django.contrib.auth import authenticate, get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny



User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer  # default for list/retrieve/update

    def get_serializer_class(self):
        """
        Use different serializers for different actions.
        """
        if self.action == 'register_user':
            return UserRegisterSerializer
        if self.action == 'login_user':
            return UserLoginSerializer
        return super().get_serializer_class()

    # ---------- REGISTER ----------
    @action(
        detail=False,
        methods=['post'],
        url_path='register',
        permission_classes=[AllowAny]
    )
    def register_user(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()

        return Response({
            "message": "User registered successfully.",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
            }
        }, status=status.HTTP_201_CREATED)

    # ---------- LOGIN ----------

    
    @action(
        detail=False,
        methods=['post'],
        url_path='login',
        permission_classes=[AllowAny]
    )
    def login_user(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            errors = {k: v[0] for k, v in serializer.errors.items()}
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data.get('email').lower()
        password = serializer.validated_data.get('password')

        # Find user by email (case-insensitive)
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid email or password."},
                            status=status.HTTP_401_UNAUTHORIZED)

        #  Check password
        if not user.check_password(password):
            return Response({"error": "Invalid email or password."},
                            status=status.HTTP_401_UNAUTHORIZED)

        #  Optional: check active flag
        if not user.is_active:
            return Response({"error": "Account disabled."},
                            status=status.HTTP_403_FORBIDDEN)

        #  Issue tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response({
            "message": "Login successful.",
            "access": access_token,
            "refresh": refresh_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
            }
        }, status=status.HTTP_200_OK)


