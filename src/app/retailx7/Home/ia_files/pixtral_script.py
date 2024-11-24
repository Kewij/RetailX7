import os
import base64
from mistralai import Mistral
import json
import pandas as pd
from typing import Union
import numpy as np
from .chat_assos import request_asos

# Load Mistral API key from environment variables
api_key = os.environ["MISTRAL_API_KEY"]

# Model specification
model = "mistral-large-latest"
small_model = "mistral-small-latest"

# Initialize the Mistral client
client = Mistral(api_key=api_key)


def img_to_base64_path(image_path):
    """Input : image_path (str) : path to the image file
    Returns : image_base64 (str) : base64 encoded image"""
    
    with open(image_path, 'rb') as image_file:
        image_bytes = image_file.read()

    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    return image_base64

def list_clothes(image_base64): 
    # Define the messages for the chat API
    messages = [
        {
            "role": "system",
            "content": "Return the answer in a JSON object with the next structure: "
                    "{\"elements\": [{\"element\": \"some name of element1\", "
                    "\"color\": \"the color of element1\", "
                    "\"fit\": \"the fit of element1 (baggy, slim...)\", "
                    "\"price\": \"some number, estimated price of element1\", "
                    "\"context\": \"one word form this list : casual, formal, athletic, office-ready, streetwear, fashion, luxury\", "
                    "\"description\": \"a description of element1, emphasizing on the vibe of the piece\"}, "
                    "{\"element\": \"some name of element2\", ...}]}"
        },
        {
            "role": "user",
            "content": "Describe each clothing piece that this person is wearing using keywords."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{image_base64}"
                }
            ]
        }
    ]

    # Call the Mistral API to complete the chat
    chat_response = client.chat.complete(
        model="pixtral-12b-2409",
        messages=messages,
        response_format={
            "type": "json_object",
        }
    )

    # Get the content of the response
    content = chat_response.choices[0].message.content
    
    return content

def recommend_from_image(image_base64, description=None):
    element = {"element":None, "color":None, "fit":None, "price":None, "context":None, "description":None}
    # Define the messages for the chat API
    messages = [
        {
            "role": "system",
            "content": "Return the answer in a JSON object with the next structure: "
                    "{\"element\": \"a clothing piece that is not in the original image\", "
                    "\"color\": \"color of this piece\", "
                    "\"fit\": \"fit of this piexe (baggy, slim...)\", "
                    "\"price\": \"some number, estimated price of the piece\", "
                    "\"context\": \"one word from this list : casual, formal, athletic, office-ready, streetwear, fashion, luxury\", "
                    "\"description\": \"a short description of the recommended piece\"}"
        },
        {
            "role": "user",
            "content": "Describe a single clothing piece following the Requirements that fit the reference image."
                    "If not precised, keep in mind the color scheme and general vibe of the reference image."
        },
        {
            "role": "user",
            "content": f"Requirements: element: {element['element']}, color: {element['color']}, fit: {element['fit']}, price: {element['price']}, context: {element['context']}, description: {element['description']}."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{image_base64}"
                }
            ]
        }
    ]

    # Call the Mistral API to complete the chat
    chat_response = client.chat.complete(
        model="pixtral-12b-2409",
        messages=messages,
        response_format={
            "type": "json_object",
        }
    )

    # Get the content of the response
    content = chat_response.choices[0].message.content
    
    return content

empty_element = {"element":None, "color":None, "fit":None, "price":None, "context":None, "description":None}

def recommend_from_wardrobe(wardrobe, element = empty_element):
    color_rule = np.random.choice([ 
                          "complementary colors: colors that are opposite on the color wheel", 
                          "analogus colors: colors that are close on the color wheel", 
                          "accent color: one bright color that pops from the rest that are neutral", 
                          "sandwiching: layering a bright color between two neutral colors",
                          "monochromatic: using different shades of the same color to create a cohesive look",
                          "pattern mixing: combining different patterns to create a unique outfit",
                          "seasonal: using seasonal colors and pieces to create a weather-appropriate outfit",
                                ])
    
    piece_rule = np.random.choice([
                            "mixing textures: incorporating different textures to add visual interest",
                            "switching styles: mixing casual and formal pieces for a unique look",
                            "statement piece: building an outfit around a bold statement piece",
                            "originality: choosing a unique piece that stands out",
                            "basics: starting with a basic piece and building around it",
                            "layering: several pieces of clothing on top of each other to add depth", 
                            "proportion balance: for example, baggy jeans with a skinny top", 
                            "accessories: adding a statement piece to elevate the outfit",
                            "dress code: following a specific dress code to create a cohesive look",
                            "comfort: prioritizing comfort while still looking put together",
                            "silouhette: creating a visually interesting shape with the outfit",
                            "jewelry: adding jewelry to elevate the outfit"
                                   ])
    # Define the messages for the chat API
    messages = [
        {
            "role": "system",
            "content": "Follow this rule when suggesting a piece of clothing: " + piece_rule
        },
        {
            "role": "system",
            "content": "Follow this rule when choosing a color: " + color_rule
        },
        {
            "role": "system",
            "content": "Return the answer in a JSON object with the next structure: "
                    "{\"elements\": [{\"element\": \"name of the piece, not too descriptive\", "
                    "\"color\": \"color of this piece, one word\", "
                    "\"fit\": \"fit of this piece\", "
                    "\"price\": \"some number, estimated price of the piece\", "
                    "\"context\": \"one word from this list : casual, formal, athletic, office-ready, streetwear, fashion, luxury\", "
                    "\"description\": \"explain why you chose this piece (don't use the word rule)\"}]}"
        },
        {
            "role": "user",
            "content": "Describe a single clothing piece or accessory following the requirements that fit in my wardrobe, while not already being in it."
        },
        {
            "role": "user",
            "content": f"Requirements: element: {element['element']}, color: {element['color']}, fit: {element['fit']}, price: {element['price']}, context: {element['context']}, description: {element['description']}."
        },
        {
            "role": "user",
            "content": f"I have these elements in my wardrobe: {(' '.join(wardrobe['description']))}."
        }
    ]

    # Call the Mistral API to complete the chat
    chat_response = client.chat.complete(
        model="mistral-large-latest",
        messages=messages,
        response_format={
            "type": "json_object",
        }
    )

    # Get the content of the response
    content = chat_response.choices[0].message.content
    
    return content

def fetch_from_img_reco(recommandations):
    query = recommandations["fit"] + " " + recommandations["color"] + " " + recommandations["element"]
    clothe = request_asos(query, maxItems=1)
    return clothe

def generate_wardrobe(new_query, user):
    prompt = """
    The user is asking you for an outfit or clothing suggestion. They may optionally indicate the number of an image they have uploaded for you to use as a reference.

    Your task is straightforward:
    1. If the user explicitly mentions an image number (e.g., "Use image 3"), return only that number as an integer.
    - Example: 3
    2. If the user does not mention any image or does not provide a clear number, return -1.

    You must **only** return the numerical value corresponding to the image number or -1. No additional information or text is needed in your response.

    **Examples:**
    - Input: "Can you use image 2 to suggest an outfit?"
    Output: 2
    - Input: "I’d like a suggestion but without using my images."
    Output: -1
    - Input: "Use photo 5 for my professional outfit."
    Output: 5
    - Input: "Suggest an outfit for winter."
    Output: -1
    """

    message = {"role": "system", "content": prompt}
    img = int(client.chat.complete(
        model="mistral-small-latest",
        messages=[message, {"role": "user", "content": new_query}]
    ).choices[0].message.content)
    print(f"Image choisie : {img}")
    images = user.user_images.all()
    if img == -1:
        # Wardrobe complète
        wardrobe = []
        for image in images:
            elements = image.description.get("elements", [])  # Récupérer "elements" ou une liste vide
            if isinstance(elements, list):  # Vérifier que c'est une liste
                wardrobe.extend(elements)  # Ajouter les éléments à la liste globale
    else:
        # Choix d'un outfit spécifique
        wardrobe = images[img-1].description["elements"]

    return wardrobe

def generate_empty_element(new_query):
    prompt = """
    The user is asking you about a specific clothing item or providing details for an outfit suggestion. Your task is to extract the relevant information from their input and return it as a dictionary with the following keys:
    - "element": The type of clothing item requested (e.g., pants, t-shirt, jacket, etc.).
    - "color": The color of the clothing item, if specified.
    - "fit": The fit or style of the clothing item (e.g., slim, oversized, tailored), if specified.
    - "price": The price or budget mentioned by the user, if specified.
    - "context": The situation or context for which the clothing item is intended (e.g., casual, professional, fitness, party), if specified.
    - "description": Any additional description of the clothing item provided by the user.

    For any key where the user does not provide enough information, set the value to `None`.

    **Examples:**
    1. Input: "I need a slim-fit black shirt for a formal event."
    Output: {
        "element": "shirt",
        "color": "black",
        "fit": "slim-fit",
        "price": None,
        "context": "formal",
        "description": None
    }

    2. Input: "Can you suggest a comfortable pair of blue jeans under $50 for casual wear?"
    Output: {
        "element": "jeans",
        "color": "blue",
        "fit": "comfortable",
        "price": 50,
        "context": "casual",
        "description": None
    }

    3. Input: "I’d like a red dress for a party, something elegant."
    Output: {
        "element": "dress",
        "color": "red",
        "fit": None,
        "price": None,
        "context": "party",
        "description": "elegant"
    }

    4. Input: "Just looking for some winter boots."
    Output: {
        "element": "boots",
        "color": None,
        "fit": None,
        "price": None,
        "context": "winter",
        "description": None
    }

    Respond strictly with the dictionary in JSON-like format. Do not include any other text or explanation.
    """

    message = {"role": "system", "content": prompt}
    empty_element = client.chat.complete(
        model="mistral-small-latest",
        messages=[message, {"role": "user", "content": new_query}],
        response_format={
            "type": "json_object",
        }
    ).choices[0].message.content
    empty_element = json.loads(empty_element)
    empty_element = {key: (None if value == "None" else value) for key, value in empty_element.items()}
    return empty_element

def pipeline_reco_from_wardrobe(new_query, user, infos_text, messages):
    wardrobe = generate_wardrobe(new_query, user)
    empty_element = generate_empty_element(new_query, messages)
    content = recommend_from_wardrobe(wardrobe, empty_element)
    clothe = fetch_from_img_reco(content)
    return clothe