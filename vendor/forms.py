from django import forms
from .models import Vendor, OpeningHour
from accounts.validators import validate_file_extension, validate_file_size

class VendorForm(forms.ModelForm):
    vendor_license = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}), validators=[validate_file_extension, validate_file_size])
    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_license']

class OpeningHourForm(forms.ModelForm):
    class Meta:
        model = OpeningHour
        fields = ['day', 'from_hour', 'to_hour', 'is_closed']