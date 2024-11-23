from .models import Image
from .models import ChatbotConversation

def user_images(request):
    if request.user.is_authenticated:
        # Récupère toutes les images de l'utilisateur connecté
        images = request.user.user_images.all().order_by('-id')
    else:
        images = []
    return {'images': images}

def chatbot_context(request):
    # Récupérer les dernières conversations du chatbot pour l'utilisateur connecté
    if request.user.is_authenticated:
        chatbot, created = ChatbotConversation.objects.get_or_create(user=request.user)
        print(chatbot)
        
        context = {
            'chatbot': chatbot,
        }
    else:
        context = {
            'chatbot': None,
        }
    return context
    