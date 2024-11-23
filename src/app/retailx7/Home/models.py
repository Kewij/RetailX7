from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    bio = models.TextField(blank=True)  # Champ texte long pour la bio de l'utilisateur
    images = models.ManyToManyField('Image', blank=True)  # Lien vers un modèle Image

class Image(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_images')
    image = models.ImageField(upload_to='user_images/')  # Téléchargement d'image
    description = models.CharField(max_length=255, blank=True)  # Description de l'image

    def __str__(self):
        return f"Image de {self.user.username}"

