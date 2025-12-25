from django import forms
from django.core.exceptions import ValidationError # <--- Import this
from django.db.models import Sum # <--- Import this
from .models import Booking
from tours.models import TourDate

class BookingForm(forms.ModelForm):
    # We add a generic field for the date selection
    tour_date = forms.ModelChoiceField(queryset=TourDate.objects.none(), label="Select Date")
    class Meta:
        model = Booking
        fields = ['number_of_people']
        widgets = {
            'number_of_people': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20}),
            'tour_date': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        # We need to filter dates so we ONLY show dates for the specific tour being booked
        tour_id = kwargs.pop('tour_id', None)
        super().__init__(*args, **kwargs)
        if tour_id:
            self.fields['tour_date'].queryset = TourDate.objects.filter(tour_id=tour_id).order_by('start_date')


    # --- NEW VALIDATION LOGIC ---
    def clean(self):
        cleaned_data = super().clean()
        tour_date = cleaned_data.get('tour_date')
        number_of_people = cleaned_data.get('number_of_people')

        if tour_date and number_of_people:
            # 1. Calculate how many seats are already taken (Pending + Confirmed)
            # We treat 'pending' as taken so we don't double-book while waiting for admin approval
            booked_seats = Booking.objects.filter(
                tour_date=tour_date, 
                status__in=['pending', 'confirmed']
            ).aggregate(Sum('number_of_people'))['number_of_people__sum'] or 0

            # 2. Check if there is space
            total_needed = booked_seats + number_of_people
            
            if total_needed > tour_date.capacity:
                available_seats = tour_date.capacity - booked_seats
                # Raise an error that will appear on the form
                raise ValidationError(f"Sorry, only {available_seats} seats are left for this date.")
        
        return cleaned_data