from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from .forms import LoginForm, ImageUploadForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ChatbotConversation

# Vue de login
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Redirection vers la page d'accueil après login
    else:
        form = AuthenticationForm()
    return render(request, 'Home/login.html', {'form': form})

# Vue de logout
def user_logout(request):
    logout(request)
    return redirect('login')  # Redirection vers la page de login après logout

# Page d'accueil
@login_required
def home(request):
    # Formulaire d'upload d'image
    if request.method == 'POST' and 'upload_image' in request.POST:
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.user = request.user
            image.save()
            return redirect('home')
    else:
        form = ImageUploadForm()
    
    return render(request, 'Home/home.html', {'form': form})


@csrf_exempt  # Ajoutez cette décorateur si vous avez des problèmes avec le CSRF pour les requêtes AJAX
@login_required
def chatbot_response(request):
    # Récupérer ou créer une conversation pour l'utilisateur connecté
    conversation, created = ChatbotConversation.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_message = request.POST.get('message')
        if user_message:
            # Ajouter le message de l'utilisateur au champ message de la conversation
            conversation.message.append({'role': 'user', 'content': user_message})

            # Exemple de réponse du chatbot
            chatbot_response = "Réponse automatique du chatbot."
            conversation.message.append({'role': 'assistant', 'content': chatbot_response})

            # Sauvegarder la conversation
            conversation.save()

            # Retourner la réponse du chatbot en JSON
            return JsonResponse({'response': chatbot_response})

    # Récupérer les messages précédents pour l'affichage
    messages = conversation.message
    return render(request, 'chatbot.html', {'chatbot': messages})
