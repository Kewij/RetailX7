from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from .forms import LoginForm, ImageUploadForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

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
def chatbot_response(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')
        
        # Traitez la logique de génération de réponse ici
        response_message = f"Vous avez dit: {user_message}"

        # Vous pouvez également ajouter la logique de votre chatbot ici
        # Par exemple, intégrer un modèle de chatbot ou utiliser une API externe
        
        return JsonResponse({'response': response_message})
