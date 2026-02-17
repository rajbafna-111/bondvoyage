from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    # columns to show
    list_display = ('id', 'user', 'tour', 'tour_date', 'total_price', 'status', 'payment_status', 'booking_date')
    
    # filters on the right sidebar
    list_filter = ('status', 'payment_status', 'booking_date', 'tour')
    
    # search bar (search by username, tour name, or transaction ID)
    search_fields = ('user__username', 'tour__name', 'transaction_id')
    
    
    readonly_fields = ('booking_date', 'total_price')
    
    fieldsets = (
        ('User & Tour', {
            'fields': ('user', 'tour', 'tour_date', 'number_of_people')
        }),
        ('Financials', {
            'fields': ('total_price', 'transaction_id', 'payment_status')
        }),
        ('Workflow', {
            'fields': ('status', 'booking_date')
        }),
    )