from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'address')
        
        # 1. Force the Address box to be small (2 rows)
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}), 
        }

    def clean_phone_number(self):
        """
        Validates the phone number:
        1. Must be digits only.
        2. Must be exactly 10 digits.
        3. Must start with 6, 7, 8, or 9.
        """
        phone = self.cleaned_data.get('phone_number')
        
        # Rule 1: Digits only
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        
        # Rule 2: Length check
        if len(phone) != 10:
            raise forms.ValidationError("Phone number must be exactly 10 digits.")
        
        # Rule 3: Valid starting digit (6, 7, 8, 9)
        if phone[0] not in ['6', '7', '8', '9']:
            raise forms.ValidationError("Invalid Phone Number.")
            
        return phone

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        
        # 2. Add Bootstrap styling to ALL fields
        for field_name in self.fields:
            existing_attrs = self.fields[field_name].widget.attrs
            existing_attrs['class'] = existing_attrs.get('class', '') + ' form-control'