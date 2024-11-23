from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Image

# Formulaire personnalisé pour le login
class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'autofocus': True}))


# Formulaire pour upload d'image
class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image', 'description']

