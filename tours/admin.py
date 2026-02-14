from django.contrib import admin
from .models import Tour, TourDate, TourImage

# --- INLINES ---
# These allow you to edit Dates and Images INSIDE the Tour page

class TourDateInline(admin.TabularInline):
    model = TourDate
    extra = 1  # Show 1 empty row by default
    classes = ['collapse']  # Click to expand (keeps the page clean)

class TourImageInline(admin.TabularInline):
    model = TourImage
    extra = 1
    classes = ['collapse']

# --- MAIN ADMIN ---

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'duration_days', 'price', 'is_active', 'updated_at')
    list_filter = ('location', 'is_active', 'duration_days')
    search_fields = ('name', 'location')
    
    # Attach the inlines here
    inlines = [TourDateInline, TourImageInline]

    # Organize fields nicely
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'location', 'description', 'image', 'is_active')
        }),
        ('Trip Details', {
            'fields': ('itinerary', 'duration_days', 'price')
        }),
    )

# We can also register these separately if you want to see a huge list of all dates
@admin.register(TourDate)
class TourDateAdmin(admin.ModelAdmin):
    list_display = ('tour', 'start_date', 'capacity', 'remaining_seats')
    list_filter = ('start_date', 'tour')