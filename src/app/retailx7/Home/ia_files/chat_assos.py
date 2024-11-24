from apify_client import ApifyClient
import matplotlib.pyplot as plt
from skimage import io
import ast

import os
from mistralai import Mistral
import json
import functools
import requests

import numpy as np
from PIL import Image as PILImage
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from Home.models import Image, InformationUser
from .pixtral_script import pipeline_reco_from_wardrobe
from .chat_stable_diff import *
from .asos_requests import request_asos_outfit

model = "mistral-small-latest"
api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)




def is_recommandation(user_input):
    prompt = "Analyze the user's input and determine if they are explicitly requesting outfit recommendations. Avoid any request containing the word 'preview'. Respond with either True or False, based solely on whether the user’s input suggests they want advice or suggestions for outfits. Do not include any punctuation in your response."
    cur_messages = [
        {"role": "system", "content": prompt},
        {"role":"user", "content":user_input}
    ]
    chat_bool = client.chat.complete(
        model=model,
        messages=cur_messages
    )
    bool_reco = chat_bool.choices[0].message.content
    return bool_reco

def make_prompt(user_input, infos_text=None):
    if infos_text == None:
        return f"""
        You are a personal fashion advisor. Your role is to provide customized fashion recommendations to users based on their preferences, occasion, and budget. Your response must only include a list of references for items that can be searched on a shopping website, formatted as a list within square brackets [].

        # Example Conversation:
        User Input:
        "I need advice on what to wear for a semi-formal dinner. I like simple, classic styles but with a modern twist. My budget is around $150."

        LLM Response:
        ["slim-fit navy blazers", "non-iron stretch Oxford shirts", "stretch slim-fit chinos", "leather loafers"]

        # User Input:
        {user_input}
        """
    else:
        return f"""
        You are a personal fashion advisor. Your role is to provide customized fashion recommendations to users based on their preferences, occasion, budget and personal information. Your response must only include a list of references for items that can be searched on a shopping website, formatted as a list within square brackets []. Based on the provided information, include the gender in your references if it is available.

        # Example Conversation:
        User Input:
        "I need advice on what to wear for a semi-formal dinner. I like simple, classic styles but with a modern twist. My budget is around $150."

        LLM Response:
        ["slim-fit navy blazers", "non-iron stretch Oxford shirts", "stretch slim-fit chinos", "leather loafers"]

        {infos_text}

        # User Input:
        {user_input}
        """

def create_first_message(outfit):
    return f"""
    Here are your recommendations to keep in memory:
    {outfit}
    Respond to the user by confirming that you have relevant recommendations. Do not explicitly reveal the details of the recommendations. Your answer must contain two sentences at most.
    """

def save_outfit_images(outfit):
    """
    Save outfit images from a list of dictionaries to the server and create Image objects.
    
    Args:
        outfit (list): List of dictionaries, each containing a NumPy image and a "url" key.

    Returns:
        None
    """
    for item in outfit:
        # Extract the NumPy image and URL
        numpy_image = item.get('image')  # Assuming this is a NumPy array
        url = item.get('url')

        if numpy_image is not None and url is not None:
            # Convert the NumPy array to a Pillow Image
            pil_image = PILImage.fromarray(numpy_image)

            # Generate a unique file name for the image
            file_name = f"{url.replace('/', '_')}.jpg"

            # Save the file to the 'image_produit_suggere' folder in MEDIA_ROOT
            folder_path = os.path.join(settings.MEDIA_ROOT, 'image_produit_suggere')
            os.makedirs(folder_path, exist_ok=True)  # Ensure the folder exists
            file_path = os.path.join(folder_path, file_name)

            # Save the Pillow image as a file
            pil_image.save(file_path)

            # Create a Django File object to save it in the Image model
            with open(file_path, 'rb') as file:
                image_content = ContentFile(file.read())

                # Create and save the Image model instance
                image_instance = Image.objects.create(
                    user=None,  # Add the user if required
                    image=image_content,  # Assign the saved image file
                    description=url  # Use the URL as the description
                )
                image_instance.save()
            
            item["image"] = image_instance
    return outfit
 
def pipeline_chatbot(user_input, infos_text=None, messages=[]):
    # Met le prompt dans le LLM
    # messages.append({"role":"user", "content":prompt})
    prompt = make_prompt(user_input, infos_text)
    print(prompt)
    chat_response = client.chat.complete(
        model=model,
        messages=[{"role":"user", "content":prompt}]
    )
    # Récupère et process les outfits donnés par le LLM
    queries = chat_response.choices[0].message.content
    print(queries)
    """
    # Pour le scrap lent
    outfit = scrap_asos_outfit(queries, maxItems=1)
    """
    # Pour le scrap rapide
    outfit = request_asos_outfit(queries, maxItems=1)
    print("outfit :", outfit)
    # outfit = save_outfit_images(outfit)
    # Créé et envoie un message à envoyer au user
    message_outfit = create_first_message(json.dumps(outfit, indent=4))
    print(message_outfit)
    messages.append({"role": "user", "content": user_input})
    messages.append({"role":"system", "content":message_outfit})
    chat_response = client.chat.complete(
        model = model,
        messages = messages
    )
    messages.append({"role": "assistant", "content": chat_response.choices[0].message.content, "dict_infos" : outfit})
    
    return messages, outfit

def transform_dict_llm(input_dict):
    if input_dict == {}:
        return None
    dict_text = "#User Infos:\n"
    for key, value in input_dict.items():
        dict_text += f"- {key.capitalize()} : {value}\n"
    return dict_text

def query_chat(new_query, user, messages=[]):
    user_infos = retrieve_information(user)
    infos_text = transform_dict_llm(user_infos)
    bool_reco = is_recommandation(new_query)
    bool_preview_outfit = is_generate_outfit(new_query)
    if bool_reco == "True" and user.user_images.exists():
        messages, _ = pipeline_reco_from_wardrobe(new_query, user, infos_text, messages)
    elif bool_reco == "True":
        messages, _ = pipeline_chatbot(new_query, infos_text, messages)
    elif bool_preview_outfit == "True":
        messages = pipeline_preview_outfit(new_query, infos_text, messages)
    else:
        messages.append({"role": "user", "content": new_query})
        response = client.chat.complete(
            model = model,
            messages = messages
        )
        messages.append({"role": "assistant", "content": response.choices[0].message.content})
    return messages

def retrieve_information(user):
    if user.is_authenticated:
        # Perform operations with the authenticated user
        print(f"Processing data for user: {user.username}")
        info_user = InformationUser.objects.get(user=user)
        return {
            "gender": info_user.gender,
            "favorite_color": info_user.favorite_color,
            "height": info_user.height,
            "weight": info_user.weight
        }
    else:
        print("Anonymous user.")
        return {}
    
def make_suggestions(user, nb_suggestions=1):
    suggestions = []
    user_infos = retrieve_information(user)
    user_infos = transform_dict_llm(user_infos)
    new_query = "Give me some nice oufits recommandations."

    while len(suggestions) < nb_suggestions:
        _, clothes = pipeline_chatbot(new_query, user_infos, [])
        suggestions += clothes
    
    return suggestions