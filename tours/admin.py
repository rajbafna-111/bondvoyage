from django.contrib import admin
from .models import *

# Create an "Inline" so dates appear inside the Tour editor
class TourDateInline(admin.TabularInline):
    model = TourDate
    extra = 1  # Shows 1 empty slot by default

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    # Columns to show in the list view
    list_display = ('name', 'location', 'price', 'duration_days', 'is_active')
    
    # Filters on the right sidebar
    list_filter = ('location', 'is_active')
    
    # Search bar
    search_fields = ('name', 'location')

    inlines = [TourDateInline]