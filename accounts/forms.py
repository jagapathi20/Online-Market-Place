from django import forms
from .models import User, UserProfile
from .validators import validate_file_extension, validate_file_size

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']
    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

class UserProfileForm(forms.ModelForm):
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter your address', 'required': 'required'}))
    profile_picture = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}), validators=[validate_file_extension, validate_file_size])
    cover_photo = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}), validators=[validate_file_extension, validate_file_size])

    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'cover_photo', 'address', 'city', 'state', 'country', 'pin_code', 'latitude', 'longitude']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['latitude'].widget.attrs['readonly'] = 'readonly'
        self.fields['longitude'].widget.attrs['readonly'] = 'readonly'


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number']
