from django import forms
from .models import Tour, TourDate

class TourForm(forms.ModelForm):
    class Meta:
        model = Tour
        fields = ['name', 'location', 'description', 'itinerary', 'duration_days', 'price', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'duration_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class TourDateForm(forms.ModelForm):
    start_date = forms.DateField(
        input_formats=['%d-%m-%Y', '%Y-%m-%d'],  # Accept both formats
        widget=forms.DateInput(
            format='%d-%m-%Y',  # Display as DD-MM-YYYY
            attrs={
                'class': 'form-control', 
                'placeholder': 'DD-MM-YYYY',
                'type': 'text',  # Force text so browser calendar doesn't override format
                'autocomplete': 'off'
            }
        )
    )

    class Meta:
        model = TourDate
        fields = ['start_date', 'capacity']
        widgets = {
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }