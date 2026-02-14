from django.db import models
from django.db.models import Sum
from ckeditor.fields import RichTextField

class Tour(models.Model):
    """
    Represents a Travel Package (e.g., 'Manali Trip', 'Goa Beach Party').
    """
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    
    description = models.TextField(help_text="Short summary for the card view")
    itinerary = RichTextField(blank=True, null=True, help_text="Detailed day-wise plan")
    
    duration_days = models.PositiveIntegerField(help_text="Total duration of the trip")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    image = models.ImageField(upload_to='tour_images/', blank=True, null=True)
    
    is_active = models.BooleanField(default=True, help_text="Uncheck to hide this tour from users")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) # Tracks when the tour was last edited

    def __str__(self):
        return self.name


class TourDate(models.Model):
    """
    Specific available dates for a Tour (e.g., Manali Trip starting on 25th Dec).
    """
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='dates')
    start_date = models.DateField()
    capacity = models.PositiveIntegerField(default=20, help_text="Total seats available for this batch")

    # --- Helper Properties ---
    
    @property
    def booked_seats(self):
        """Calculates how many people have booked this specific date."""
        # We import inside the method to avoid "Circular Import" errors
        from bookings.models import Booking 
        
        total_booked = Booking.objects.filter(
            tour_date=self, 
            status__in=['Pending', 'Confirmed']
        ).aggregate(Sum('number_of_people'))['number_of_people__sum']
        
        return total_booked or 0  # Return 0 if no bookings exist

    @property
    def remaining_seats(self):
        """Calculates seats left."""
        return self.capacity - self.booked_seats

    def __str__(self):
        """
        Returns a string like: '25 Dec 2025 (4 seats left)'
        """
        left = self.remaining_seats
        date_str = self.start_date.strftime('%d %b %Y')
        
        if left <= 0:
            return f"{date_str} (SOLD OUT)"
        else:
            return f"{date_str} ({left} seats left)"


class TourImage(models.Model):
    """
    Additional Gallery Images for a Tour.
    """
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='tour_gallery/')
    
    def __str__(self):
        return f"Gallery Image for {self.tour.name}"