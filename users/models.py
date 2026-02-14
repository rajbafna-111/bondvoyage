from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Custom User Model for BondVoyage.
    Extends Django's default User to include Roles, Phone, and Address.
    """
    
    # --- Role Constants ---
    # We define these as constants to avoid typos in our code later
    ADMIN = 'admin'
    CUSTOMER = 'customer'
    
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (CUSTOMER, 'Customer'),
    ]
    
    # --- Custom Fields ---
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
        # Shows "rajbafna111 (Admin)" in the admin panel
        return f"{self.username} ({self.get_role_display()})"

    # --- Helper Properties ---
    # These make it super easy to check roles in templates and views!
    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_customer(self):
        return self.role == self.CUSTOMER