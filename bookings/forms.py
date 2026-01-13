from django import forms
from django.core.exceptions import ValidationError 
from django.db.models import Sum
from .models import Booking
from tours.models import TourDate

class BookingForm(forms.ModelForm):
    # We add a generic field for the date selection
    tour_date = forms.ModelChoiceField(queryset=TourDate.objects.none(), label="Select Date", widget=forms.Select(attrs={'class': 'form-select'}))
    
    class Meta:
        model = Booking
        fields = ['number_of_people']
        widgets = {
            'number_of_people': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20}),
        }

    def __init__(self, *args, **kwargs):
        # --- FIX IS HERE ---
        # 1. We must pop 'tour' because that is what the View sends.
        self.tour = kwargs.pop('tour', None) 
        
        super().__init__(*args, **kwargs)
        
        # 2. Use the extracted tour object to filter the dates
        if self.tour:
            self.fields['tour_date'].queryset = TourDate.objects.filter(tour=self.tour).order_by('start_date')


    # --- VALIDATION LOGIC (This part was already perfect) ---
    def clean(self):
        cleaned_data = super().clean()
        tour_date = cleaned_data.get('tour_date')
        number_of_people = cleaned_data.get('number_of_people')

        if tour_date and number_of_people:
            # 1. Calculate how many seats are already taken
            booked_seats = Booking.objects.filter(
                tour_date=tour_date, 
                status__in=['Pending', 'Confirmed'] # check capitalization!
            ).aggregate(Sum('number_of_people'))['number_of_people__sum'] or 0

            # 2. Check if there is space
            total_needed = booked_seats + number_of_people
            
            if total_needed > tour_date.capacity:
                available_seats = tour_date.capacity - booked_seats
                raise ValidationError(f"Sorry, only {available_seats} seats are left for this date.")
        
        return cleaned_data