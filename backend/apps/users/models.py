"""
Custom User model for HMS.
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from apps.core.models import UUIDModel


class UserManager(BaseUserManager):
    """Custom user manager for HMS."""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')
        return self.create_user(email, password, **extra_fields)


class User(UUIDModel, AbstractUser):
    """
    Custom User model with email as the primary identifier.
    """
    USER_TYPE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('clinic_admin', 'Clinic Admin'),
        ('admin', 'System Admin'),
    ]
    
    username = None
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='patient')
    
    # Profile fields
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='India')
    postal_code = models.CharField(max_length=20, blank=True)
    
    # WhatsApp opt-in
    whatsapp_number = models.CharField(max_length=20, blank=True)
    whatsapp_opted_in = models.BooleanField(default=False)
    
    # Verification
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    
    # Timestamps
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.email} ({self.user_type})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email
