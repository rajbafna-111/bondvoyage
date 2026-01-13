from django.contrib import admin
from .models import *

# 1. Inline for DATES
class TourDateInline(admin.TabularInline):
    model = TourDate
    extra = 1

# 2. Inline for IMAGES (Gallery)
class TourImageInline(admin.TabularInline):
    model = TourImage
    extra = 3

# 3. Main Tour Admin (Combined)
@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'price', 'duration_days', 'is_active')
    list_filter = ('location', 'is_active')
    search_fields = ('name', 'location')
    
    inlines = [TourDateInline, TourImageInline]