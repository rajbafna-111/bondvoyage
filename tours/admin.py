from django.contrib import admin
from .models import Tour, TourDate, TourImage

class TourDateInline(admin.TabularInline):
    model = TourDate
    extra = 1 
    classes = ['collapse'] 

class TourImageInline(admin.TabularInline):
    model = TourImage
    extra = 1
    classes = ['collapse']

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'duration_days', 'price', 'is_active', 'updated_at')
    list_filter = ('location', 'is_active', 'duration_days')
    search_fields = ('name', 'location')
    
    inlines = [TourDateInline, TourImageInline]

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'location', 'description', 'image', 'is_active')
        }),
        ('Trip Details', {
            'fields': ('itinerary', 'duration_days', 'price')
        }),
    )

@admin.register(TourDate)
class TourDateAdmin(admin.ModelAdmin):
    list_display = ('tour', 'start_date', 'capacity', 'remaining_seats')
    list_filter = ('start_date', 'tour')