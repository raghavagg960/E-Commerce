from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import Category, Brand, Product, Review
from .serializers import (
    CategorySerializer,
    BrandSerializer,
    ProductSerializer,
    ReviewSerializer,
)
from django.contrib.auth import get_user_model

User = get_user_model()


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
 

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True)

        category_id = self.request.query_params.get('category')
        brand_id = self.request.query_params.get('brand')
        search = self.request.query_params.get('search')

        if category_id:
            qs = qs.filter(category_id=category_id)
        if brand_id:
            qs = qs.filter(brand_id=brand_id)
        if search:
            qs = qs.filter(name__icontains=search)

        return qs

    def perform_create(self, serializer):
        user = self.request.user

        # Only vendors can create products
        if not user.is_authenticated or user.role != 'vendor':
            return Response(
                {"detail": "Only vendors can create products."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not hasattr(user, 'vendor_profile'):
             raise ValidationError("No vendor profile found for this user.")
        
        vendor_profile = user.vendor_profile

        # If vendor is User:
        serializer.save(vendor=vendor_profile)

        # If vendor is VendorProfile instead:
        # serializer.save(vendor=user.vendor_profile)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


