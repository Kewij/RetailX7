from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Image, InformationUser

# Formulaire personnalisé pour le login
class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'autofocus': True}))


# Formulaire pour upload d'image
class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']

class InformationUserForm(forms.ModelForm):
    class Meta:
        model = InformationUser
        fields = ['gender', 'favorite_color', 'height', 'weight']
        widgets = {
            'gender': forms.Select(choices=[
                ('Male', 'Male'),
                ('Female', 'Female'),
                ('Other', 'Other'),
            ]),
            'favorite_color': forms.TextInput(attrs={
                'placeholder': 'Enter your favorite color'
            }),
            'height': forms.NumberInput(attrs={
                'placeholder': 'Enter your height in cm'
            }),
            'weight': forms.NumberInput(attrs={
                'placeholder': 'Enter your weight in kg'
            }),
        }