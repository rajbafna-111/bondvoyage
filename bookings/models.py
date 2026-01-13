from django.db import models
from django.conf import settings
from tours.models import *

class Booking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ]

    # Link to the User
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Link to the specific Tour
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)

    tour_date = models.ForeignKey(TourDate, on_delete=models.CASCADE, null=True, blank=True)
    
    number_of_people = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    booking_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True, help_text="Payment Reference ID")

    def save(self, *args, **kwargs):
        # Auto-calculate total price before saving
        if not self.total_price:
            self.total_price = self.tour.price * self.number_of_people
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.tour.name}"