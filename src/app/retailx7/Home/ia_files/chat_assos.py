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
from Home.models import Image

model = "mistral-small-latest"
api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)


def is_recommandation(user_input):
    prompt = "Analyze the user's input and determine if they are explicitly requesting outfit recommendations. Respond with either True or False, based solely on whether the user’s input suggests they want advice or suggestions for outfits. Do not include any punctuation in your response."
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

def make_prompt(user_input):
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


def scrap_asos(query, maxItems = 3):
    """ Data scraper from asos.
    Inputs: 
        query (str): search query
        maxItems (int): number of items to scrap
    
    Returns:
        Items (list): list of dictionaries containing the following keys:
            name (str): name of the item
            brandName (str): brand name of the item
            price (str): price of the item
            image (np.array): image of the item
            url (str): url of the item
            gender (str): gender of the item
    """
    
    client = ApifyClient("apify_api_zHwEmmY3hZNab6L57n4NiebpEJDQy42PNRGq")
    
    run_input = {
        "search": query,
        "maxItems": maxItems,
        "endPage": 1,
        "extendOutputFunction": "($) => { return {} }",
        "customMapFunction": "(object) => { return {...object} }",
        "proxy": { "useApifyProxy": True },
    }
    
    run = client.actor("epctex/asos-scraper").call(run_input=run_input)
    
    Items = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        try :
            # Certains articles n'ont pas de prix d'où la gestion d'erreur
            price = item["variants"][0]["pricing"]["price"]["current"]["text"]
            
            Items.append({
                "name" : item["name"],
                "brandName" : item["brandName"],
                "price" : price,
                "image" : io.imread(item["images"][0]["url"]),
                "gender" : item["gender"],
                "url" : item["url"]
            })
        except:
            pass
        
    return Items

def scrap_asos_outfit(queries, maxItems=3):
    queries = ast.literal_eval(queries)
    outfit = []
    for i, query in enumerate(queries):
        clothe = scrap_asos(query, maxItems)
        outfit += clothe
    return outfit

def request_asos(query, maxItems=3):
    
	url = "https://asos2.p.rapidapi.com/products/v2/list"

	querystring = {"store":"US","offset":"0","q": query,"limit": str(maxItems), "country":"US","sort":"freshness","currency":"USD","sizeSchema":"US","lang":"en-US"}

	headers = {
		"x-rapidapi-key": "7c2a2e3244msh805418e285d23cbp1faaa8jsn691342a23625",
		"x-rapidapi-host": "asos2.p.rapidapi.com"
	}

	response = requests.get(url, headers=headers, params=querystring)

	response = response.json()
	response = response["products"]

	list_keys = ["name", "url", "price", "imageUrl", "brandName", "price"]
	processed_response = []
	for product in response:
		processed_product = {}
		for key in list_keys:
			processed_product[key] = product[key]
		processed_product["price"] = processed_product["price"]["current"]["text"]
		processed_response.append(processed_product)
	return processed_response

def request_asos_outfit(queries, maxItems=3):
    queries = ast.literal_eval(queries)
    outfit = []
    for i, query in enumerate(queries):
        clothe = request_asos(query, maxItems)
        outfit += clothe
    return outfit

def create_first_message(outfit):
    return f"""
    Here are your recommendations to keep in memory:
    {outfit}
    Respond to the user by confirming that you have relevant recommendations. Do not explicitly reveal the details of the recommendations.
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
 
def pipeline_chatbot(user_input, messages=[]):
    # Met le prompt dans le LLM
    # messages.append({"role":"user", "content":prompt})
    prompt = make_prompt(user_input)
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
    
    return messages

def query_chat(new_query, messages=[]):
    bool_reco = is_recommandation(new_query)
    if bool_reco == "True":
        messages = pipeline_chatbot(new_query, messages)
    else:
        messages.append({"role": "user", "content": new_query})
        response = client.chat.complete(
            model = model,
            messages = messages
        )
        messages.append({"role": "assistant", "content": response.choices[0].message.content})
    return messages
