from django.db import models
from django.conf import settings
from tours.models import Tour, TourDate

class Booking(models.Model):
    # 1. Updated Booking Workflow Statuses
    STATUS_CHOICES = [
        ('Pending', 'Pending Verification'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),  # <-- Added Completed
    ]

    # 2. New Payment Workflow Statuses
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Payment Pending'),
        ('Paid', 'Payment Verified'),
        ('Rejected', 'Payment Rejected'),
        ('Refunded', 'Payment Refunded'),
    ]

    # Links
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    tour_date = models.ForeignKey(TourDate, on_delete=models.CASCADE, null=True, blank=True)
    
    # Details
    number_of_people = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Status Fields
    # I kept the name 'status' to save you from complex migrations, 
    # but updated the choices.
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # NEW FIELD: Tracks the money specifically
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    
    booking_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True, help_text="Payment Reference ID")

    def save(self, *args, **kwargs):
        # Auto-calculate total price before saving
        if not self.total_price and self.tour and self.number_of_people:
            self.total_price = self.tour.price * self.number_of_people
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.tour.name} ({self.status})"