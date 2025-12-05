from rest_framework import serializers
from .models import Category, Brand, Product, ProductImage, Review
from django.contrib.auth import get_user_model

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'parent',
            'image',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'logo',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_main']
        read_only_fields = ['id']


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source='category',
        queryset=Category.objects.all(),
        write_only=True
    )

    brand = BrandSerializer(read_only=True)
    brand_id = serializers.PrimaryKeyRelatedField(
        source='brand',
        queryset=Brand.objects.all(),
        required=False,
        allow_null=True,
        write_only=True
    )

    images = ProductImageSerializer(many=True, read_only=True)

    # vendor info (short)
    vendor = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'price',
            'discount_price',
            'stock',
            'is_active',
            'created_at',
            'updated_at',
            'category',
            'category_id',
            'brand',
            'brand_id',
            'vendor',
            'images',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'vendor']

    def get_vendor(self, obj):
        # if vendor is User
        if hasattr(obj.vendor, 'email'):
            return {
                "id": obj.vendor.id,
                "email": obj.vendor.email,
                "name": obj.vendor.first_name,
            }
        # if vendor is VendorProfile
        return {
            "id": obj.vendor.id,
            "shop_name": getattr(obj.vendor, "shop_name", ""),
        }
