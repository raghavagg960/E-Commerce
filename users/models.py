from django.db import models
from django.contrib.auth.models import AbstractUser
from ecommerce import settings
from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):

    username = None
    
    ROLE_CHOICES = [
    ('customer', 'Customer'),
    ('vendor', 'Vendor'),
    ('admin', 'Admin'),
]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    mobile_no = models.CharField(max_length=10, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'mobile_no']
    objects = UserManager()   

    def __str__(self):
        return self.first_name
    
    class Meta:
        db_table = "Users"
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class VendorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vendor_profile'
    )

    # Essential Vendor Details
    shop_name = models.CharField(max_length=255)
    gst_number = models.CharField(max_length=50, blank=True, null=True)
    pan_number = models.CharField(max_length=20, blank=True, null=True)

    # Addresses
    registered_address = models.TextField(blank=True, null=True)
    pickup_address = models.TextField(blank=True, null=True)

    # Contact
    shop_phone = models.CharField(max_length=15, blank=True, null=True)

    # Bank Details (good for realism)
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.shop_name} ({self.user.email})"
    
    class Meta:
        db_table = 'Vendor Profile'
        managed = True
        verbose_name = 'Vendor Profile'
        verbose_name_plural = 'Vendor Profile'


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.country}"
    
    class Meta:
        db_table = 'Address'
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
