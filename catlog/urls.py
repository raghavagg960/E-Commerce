from django.urls import path
from .views import (
    CategoryViewSet,
    BrandViewSet,
    ProductViewSet,
    ReviewViewSet,
)

# ---------- CATEGORY ----------
category_list = CategoryViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
category_detail = CategoryViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

# ---------- BRAND ----------
brand_list = BrandViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
brand_detail = BrandViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

# ---------- PRODUCT ----------
product_list = ProductViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
product_detail = ProductViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

# ---------- REVIEW ----------
review_list = ReviewViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
review_detail = ReviewViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

urlpatterns = [
    # Categories
    path('categories/', category_list, name='category-list'),
    path('categories/<int:pk>/', category_detail, name='category-detail'),

    # Brands
    path('brands/', brand_list, name='brand-list'),
    path('brands/<int:pk>/', brand_detail, name='brand-detail'),

    # Products
    path('products/', product_list, name='product-list'),
    path('products/<int:pk>/', product_detail, name='product-detail'),

    # Reviews
    path('reviews/', review_list, name='review-list'),
    path('reviews/<int:pk>/', review_detail, name='review-detail'),
]
