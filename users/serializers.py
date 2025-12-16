from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import VendorProfile, User


User = get_user_model()



  
class VendorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfile
        # don't expose user here; we’ll attach it in the view/parent serializer
        fields = [
            'id',
            'shop_name',
            'gst_number',
            'pan_number',
            'registered_address',
            'pickup_address',
            'shop_phone',
            'bank_account_number',
            'ifsc_code',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    # include vendor profile when viewing a user (read-only)
    vendor_profile = VendorProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'mobile_no',
            'role',
            'vendor_profile',
        ]

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    vendor_profile = VendorProfileSerializer(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'mobile_no',
            'password',
            'role',
            'vendor_profile',
        ]

    def validate(self, data):
        errors = {}

        # Custom required field checks
        required_fields = {
            "first_name": "First name is required.",
            "last_name": "Last name is required.",
            "email": "Email is required.",
            "password": "Password is required.",
            "mobile_no": "Mobile number is required.",
        }

        for field, msg in required_fields.items():
            if not data.get(field):
                errors[field] = msg

        # Additional custom validations
        if data.get("password") and len(data["password"]) < 8:
            errors["password"] = "Password must be at least 8 characters long."

        # role handling (default to customer if missing)
        role = data.get("role") or "customer"
        data["role"] = role  # ensure role is set in validated_data

        vendor_data = data.get("vendor_profile")

        # if vendor → vendor_profile must be provided
        if role == "vendor":

            if not vendor_data:
                errors["vendor_profile"] = "Vendor details are required when registering as a vendor."
            else:
                vendor_errors = {}

                gst = vendor_data.get("gst_number")
                pan = vendor_data.get("pan_number")
                account = vendor_data.get("bank_account_number")
                phone = vendor_data.get("shop_phone")
                reg_addr = vendor_data.get("registered_address")
                pickup_addr = vendor_data.get("pickup_address")

                if gst and VendorProfile.objects.filter(gst_number__iexact=gst).exists():
                    vendor_errors["gst_number"] = "This GST number is already registered."

                if pan and VendorProfile.objects.filter(pan_number__iexact=pan).exists():
                    vendor_errors["pan_number"] = "This PAN number is already registered."

                if account and VendorProfile.objects.filter(bank_account_number=account).exists():
                    vendor_errors["bank_account_number"] = "This bank account number is already registered."

                if phone and VendorProfile.objects.filter(shop_phone=phone).exists():
                    vendor_errors["shop_phone"] = "This shop phone number is already registered."

                if reg_addr and VendorProfile.objects.filter(
                    registered_address__iexact=reg_addr
                ).exists():
                    vendor_errors["registered_address"] = "This registered address is already registered."

                if pickup_addr and VendorProfile.objects.filter(
                    pickup_address__iexact=pickup_addr
                ).exists():
                    vendor_errors["pickup_address"] = "This pickup address is already registered."

                if vendor_errors:
                    errors["vendor_profile"] = vendor_errors


        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        # pull out nested vendor data before creating user
        vendor_data = validated_data.pop('vendor_profile', None)
        role = validated_data.get('role', 'customer')

        # hash password (same style you used)
        validated_data["password"] = make_password(validated_data["password"])
        user = super().create(validated_data)

        # if this user is a vendor, create VendorProfile
        if role == "vendor" and vendor_data:
            VendorProfile.objects.create(user=user, **vendor_data)

        return user




class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


  