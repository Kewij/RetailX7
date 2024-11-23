from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Image

# Formulaire pour upload d'image
class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image', 'description']

