from django.db import models
from django.db.models import Sum

class Tour(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    duration_days = models.PositiveIntegerField(help_text="How many days is this tour?")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='tour_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class TourDate(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='dates')
    start_date = models.DateField()
    capacity = models.PositiveIntegerField(default=20, help_text="Max people allowed")
    
    def __str__(self):
        return f"{self.start_date.strftime('%d %b %Y')}"
    
    def __str__(self):
        # Calculate booked seats
        from bookings.models import Booking 
        
        booked = Booking.objects.filter(
            tour_date=self, 
            status__in=['pending', 'confirmed']
        ).aggregate(Sum('number_of_people'))['number_of_people__sum'] or 0
        
        remaining = self.capacity - booked
        
        if remaining <= 0:
            return f"{self.start_date.strftime('%d %b %Y')} (SOLD OUT)"
        else:
            return f"{self.start_date.strftime('%d %b %Y')} ({remaining} seats left)"
