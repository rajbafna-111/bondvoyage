from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Use the default UserAdmin but attach our custom model
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # What columns to show in the list
    list_display = ('username', 'email', 'role', 'phone_number', 'is_staff')
    
    # What filters to show on the right side
    list_filter = ('role', 'is_staff', 'is_superuser', 'date_joined')
    
    # Fields to search
    search_fields = ('username', 'email', 'phone_number')
    
    # Organize the "Edit User" page
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone_number', 'address')}),
    )