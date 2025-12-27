from django.contrib import admin
from .models import Booking

# Define the action function
def mark_confirmed(modeladmin, request, queryset):
    queryset.update(status='confirmed')
mark_confirmed.short_description = "Mark selected bookings as Confirmed"

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'tour', 'status', 'total_price', 'booking_date')
    list_filter = ('status', 'booking_date')
    search_fields = ('user__username', 'tour__name')
    actions = [mark_confirmed]