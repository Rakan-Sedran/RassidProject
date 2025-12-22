from django import forms
from .models import SubscriptionRequest

class AirportSignupForm(forms.ModelForm):
    class Meta:
        model = SubscriptionRequest
        fields = [
            'airport_name', 'airport_code', 'country', 'city',
            'admin_email', 'admin_phone', 'selected_plan',
            'official_license', 'commercial_record'
        ]
        widgets = {
            'airport_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Airport Name'}),
            'airport_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IATA Code (e.g. RUH)'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'admin_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Official Contact Email'}),
            'admin_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+966...'}),
            'selected_plan': forms.Select(attrs={'class': 'form-control'}),
            'official_license': forms.FileInput(attrs={'class': 'form-control-file'}),
            'commercial_record': forms.FileInput(attrs={'class': 'form-control-file'}),
        }