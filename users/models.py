from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Custom User Model for BondVoyage.
    Extends Django's default User to include Roles, Phone, and Address.
    """
    
    ADMIN = 'admin'
    CUSTOMER = 'customer'
    
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (CUSTOMER, 'Customer'),
    ]
    
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default=CUSTOMER,
        help_text="Designates the user's privilege level."
    )
    
    phone_number = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        help_text="Contact number for booking updates."
    )
    
    address = models.TextField(
        blank=True, 
        null=True,
        help_text="Residential address for billing."
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_customer(self):
        return self.role == self.CUSTOMER