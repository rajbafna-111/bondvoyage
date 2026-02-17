from django.db import models
from django.conf import settings
from tours.models import Tour, TourDate

class Booking(models.Model):
    # Workflow: Pending -> Confirmed -> Completed (or Cancelled)
    STATUS_CHOICES = [
        ('Pending', 'Pending Verification'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    ]

    # Payment: Pending -> Paid (or Rejected/Refunded)
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Payment Pending'),
        ('Paid', 'Payment Verified'),
        ('Rejected', 'Payment Rejected'),
        ('Refunded', 'Payment Refunded'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    
    tour = models.ForeignKey(
        Tour, 
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    
    tour_date = models.ForeignKey(
        TourDate, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='bookings',
        help_text="The specific date batch the user has chosen"
    )

    number_of_people = models.PositiveIntegerField(default=1)
    
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Auto-calculated: Price x People"
    )
    
    transaction_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        help_text="Payment Reference ID (e.g., UPI Transaction ID)"
    )

    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Pending'
    )
    
    payment_status = models.CharField(
        max_length=20, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='Pending'
    )
    
    booking_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.tour and self.number_of_people:
            self.total_price = self.tour.price * self.number_of_people
        super().save(*args, **kwargs)

    def __str__(self):
        return f"#{self.id} | {self.user.username} - {self.tour.name} ({self.status})"