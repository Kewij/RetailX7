from .models import Image

def user_images(request):
    if request.user.is_authenticated:
        # Récupère toutes les images de l'utilisateur connecté
        images = request.user.user_images.all()
    else:
        images = []
    return {'images': images}