from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    bio = models.TextField(blank=True)  # Champ texte long pour la bio de l'utilisateur
    images = models.ManyToManyField('Image', blank=True)  # Lien vers un modèle Image
    information = models.JSONField(blank=True, null=True)  # Field to store user information as a dictionary

    groups = models.ManyToManyField(
        'auth.Group', 
        related_name='customuser_groups',  # Le related_name personnalisé
        blank=True,
        help_text='The groups this user belongs to.'
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions',  # Le related_name personnalisé
        blank=True,
        help_text='Specific permissions for this user.'
    )

class Image(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Utilisation du modèle d'utilisateur personnalisé (CustomUser)
        on_delete=models.CASCADE,
        related_name='user_images'  # Ce related_name permet d'accéder aux images via user.user_images.all()
    )
    image = models.ImageField(upload_to='user_images/')
    description = models.JSONField(blank=True)

    def __str__(self):
        return f"Image {self.id} de {self.user.username}"
    

class ChatbotConversation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.JSONField(default=list) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation with {self.user.username} at {self.created_at}"

