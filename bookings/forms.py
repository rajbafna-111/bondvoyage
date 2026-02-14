from django import forms
from django.core.exceptions import ValidationError 
from django.db.models import Sum
from datetime import date 
from .models import Booking
from tours.models import TourDate

class BookingForm(forms.ModelForm):
    tour_date = forms.ModelChoiceField(
        queryset=TourDate.objects.none(), # Empty by default, populated in __init__
        label="Select Date", 
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Booking
        fields = ['number_of_people']
        widgets = {
            'number_of_people': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20}),
        }

    def __init__(self, *args, **kwargs):
        """
        Dynamically filter the date dropdown based on the specific Tour.
        """
        self.tour = kwargs.pop('tour', None) 
        super().__init__(*args, **kwargs)
        
        if self.tour:
            # Show dates for THIS tour that are in the FUTURE
            self.fields['tour_date'].queryset = TourDate.objects.filter(
                tour=self.tour,
                start_date__gte=date.today()
            ).order_by('start_date')

    def clean(self):
        """
        Validate Seat Availability.
        Prevents overbooking.
        """
        cleaned_data = super().clean()
        tour_date = cleaned_data.get('tour_date')
        number_of_people = cleaned_data.get('number_of_people')

        if tour_date and number_of_people:
            # Calculate currently booked seats for this specific date
            booked_seats = Booking.objects.filter(
                tour_date=tour_date, 
                status__in=['Pending', 'Confirmed']
            ).aggregate(Sum('number_of_people'))['number_of_people__sum'] or 0

            total_needed = booked_seats + number_of_people
            
            if total_needed > tour_date.capacity:
                available_seats = tour_date.capacity - booked_seats
                
                if available_seats <= 0:
                    raise ValidationError("Sorry, this date is fully booked.")
                else:
                    raise ValidationError(f"Sorry, only {available_seats} seats are left for this date.")
        
        return cleaned_data