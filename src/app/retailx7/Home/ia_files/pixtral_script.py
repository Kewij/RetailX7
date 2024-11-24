import os
import base64
from mistralai import Mistral
import json
import pandas as pd
from typing import Union
import numpy as np
from .asos_requests import request_asos

# Load Mistral API key from environment variables
api_key = os.environ["MISTRAL_API_KEY"]

# Model specification
model = "mistral-large-latest"
small_model = "mistral-small-latest"

# Initialize the Mistral client
client = Mistral(api_key=api_key)

def json_to_dataframe(json_data: Union[str, dict], key: str = None) -> pd.DataFrame:
    # If json_data is a string, parse it into a dictionary
    if isinstance(json_data, str):
        json_data = json.loads(json_data)
    
    # If a key is provided, extract the list of records from the JSON object
    if key is not None:
        data = json_data[key]
    else:
        data = json_data
    
    # Convert the list of records to a pandas DataFrame
    df = pd.DataFrame(data)
    
    return df

def img_to_base64_path(image_path):
    """Input : image_path (str) : path to the image file
    Returns : image_base64 (str) : base64 encoded image"""
    
    with open(image_path, 'rb') as image_file:
        image_bytes = image_file.read()

    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    return image_base64

def list_clothes(args): 
    image_base64 = args
    path = os.path.dirname(__file__)
    path=os.path.join(path,"guides","desc_guide.txt")
    with open(path, "r") as f:
        guide = f.read()
        
    # Define the messages for the chat API
    messages = [
        {
            "role": "system",
            "content": "Return the answer in a JSON object with the next structure: "
                    "{\"elements\": [{\"element\": \"some name for element1\", "
                    "\"color\": \"the color of element1\", "
                    "\"fit\": \"the fit, shape of element1. Be concise.\", "
                    "\"price\": \"some number, estimated price of element1\", "
                    "\"context\": \"a word describing the occasion, mood or functionality of the piece\", "
                    "\"description\": \"a description of element1, emphasizing on the vibe of the piece and that encapsulates the precedent variables\"}, "
                    "{\"element\": \"some name for element2\", ...}]}"
        },
        {
            "role": "system",
            "content": f"You are a fashion critique, neutral and objective.\n\n {guide} \n\n You are presented with an image of an outfit, describe each of the elements thanks to your expertise "
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
        temperature=0.4,
        response_format={
            "type": "json_object",
        }
    )

    # Get the content of the response
    content = chat_response.choices[0].message.content
    
    return content

def process_critique(args):
    wardrobe, model = args
    path = os.path.dirname(__file__)
    path=os.path.join(path,"guides","critique_guide.txt")
    with open(path, "r") as f:
        guide = f.read()
    
    chat_response = client.chat.complete(
        model=f"mistral-{model}-latest",
        messages=[
            {"role": "system", "content": f"As a 'Fashion Critique', your mission is to help relook people. \n\n {guide} \n\n You are given a description of items in an outfit. Give a critique of the outfit, outlining the general vibe, how the pieces work together and what could be improved."},
            {"role": "user", "content": '-'+'\n-'.join(wardrobe['description'])},
        ],
        temperature=0.2,
        max_tokens=2048
    )
    result = chat_response.choices[0].message.content

    return result

def recommend_item(args):
    critique, color_rule, piece_rule, element, model = args  
    image_base64 = args
    path = os.path.dirname(__file__)
    path=os.path.join(path,"guides","desc_guide.txt")
    with open(path, "r") as f:
        guide = f.read()
    # Define the messages for the chat API
    messages = [
        {
            "role": "system",
            "content": "Return the answer in a JSON object with the next structure: "
                    "{\"elements\": [{\"element\": \"some short name for element1\", "
                    "\"color\": \"the color of element1\", "
                    "\"fit\": \"the fit, shape of element1\", "
                    "\"price\": \"some number, estimated price of element1\", "
                    "\"context\": \"a word describing the occasion, mood or functionality of the piece\", "
                    "\"description\": \"a description of element1, emphasizing on the vibe of the piece and that encapsulates the precedent variables\"}]}"
        },
        {
            "role": "system",
            "content": f"You are a fashion critique, neutral and objective.\n\n {guide} \n\n You are presented with a critique of an outfit, describe a single element that would improve the outfit."
        },
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
            "content": "You will have to strictly follow these constraints when designing the item :" + str(element)
        },
        {
            "role": "user",
            "content": critique
        }
    ]

    # Call the Mistral API to complete the chat
    chat_response = client.chat.complete(
        model=f"mistral-{model}-latest",
        messages=messages,
        temperature=0.4,
        response_format={
            "type": "json_object",
        }
    )

    # Get the content of the response
    content = chat_response.choices[0].message.content
    
    return content

def recommend_from_wardrobe(args):
    wardrobe, element = args
    model="large"
    color_rules = np.random.choice([ 
                                "complementary colors: colors that are opposite on the color wheel", 
                                "analogus colors: colors that are close on the color wheel", 
                                "accent color: one bright color that pops from the rest that are neutral", 
                                "sandwiching: layering a bright color between two neutral colors",
                                "monochromatic: using different shades of the same color to create a cohesive look",
                                "pattern mixing: combining different patterns to create a unique outfit",
                                "seasonal: using seasonal colors and pieces to create a weather-appropriate outfit",
                                            ])
            
    piece_rules = np.random.choice([
                                    "mixing textures: incorporating different textures to add visual interest",
                                    "statement piece: building an outfit around a bold statement piece",
                                    "proportion balance: suggest a piece with a fit that balances the outfit", 
                                    "accessories: adding an accessory to elevate the outfit",
                                    "silouhette: creating a visually interesting shape with the outfit",
                                    "replacement: suggesting a piece that would replace a current piece in the outfit",
                                    "layering: adding a layer to the outfit to create depth, like a coat or jacket",
                                    "adding surface: suggest a pig piece with a different surface, like a shiny or matte fabric"
                                        ])
    
    critique = process_critique((wardrobe, model))
    content = recommend_item((critique, color_rules, piece_rules, element, model))
    
    return content

def fetch_from_img_reco(recommandations):
    query = recommandations["fit"] + " " + recommandations["color"] + " " + recommandations["element"]
    clothe = request_asos(query, maxItems=1)
    return clothe

def generate_wardrobe(new_query, user):
    messages = [
        {
            "role": "system",
            "content": "Return the answer as a single number, either positive or -1 but nothing else. ,"
                        "You must **only** return the numerical value corresponding to the image number. No additional information or text is needed in your response."
                        "If there is no number in the prompt, you will return -1. Never return -1 if there is a number in the prompt."
        },
        {
            "role": "system",
            "content": "1. If the user explicitly mentions an image number (e.g., 'image 1' or 'picture 4' or 'photo 2'), return only that number as an integer. ,"
                        "2. If the user does not mention any image or does not provide a clear number, return -1."
        },
        {
            "role": "user",
            "content": new_query
        }
    ]

    img = client.chat.complete(
        model="mistral-small-latest",
        messages=messages
    ).choices[0].message.content
    
    print(f"Image choisie : {img}")
    img = int(img)
    
    
    images = user.user_images.all()
    if img > 0:
        print("Description choisie :", images[img-1].description["elements"])
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

    return {"elements": wardrobe}, img

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

def create_reco_message(outfit, desc):
    return f"""
    Here is your recommendation to keep in memory:
    {outfit}.
    Your task is to indicate that a recommendation has been successfully found and to provide the exact description stored in the variable `desc`. Follow these instructions:

    1. Begin your response with a natural and varied sentence indicating that you have found a recommendation.
    2. Immediately after, output the value of the variable `desc` exactly as it is. Do not alter, rephrase, or add anything to the description.
    3. Your response must be limited to these two parts: the introductory sentence and the exact content of `desc`.

    **Example:**

    If `desc` is: "A stylish slim-fit black blazer perfect for formal meetings and professional events."
    Your output should be:
    I’ve found something that might interest you.
    A stylish slim-fit black blazer perfect for formal meetings and professional events.

    If `desc` is: "Comfortable blue running shoes with great support for long-distance runs."
    Your output should be:
    Here’s a recommendation based on your request.
    Comfortable blue running shoes with great support for long-distance runs.

    If `desc` is: "An elegant red cocktail dress ideal for evening parties and special occasions."
    Your output should be:
    This is a suggestion that matches what you’re looking for.
    An elegant red cocktail dress ideal for evening parties and special occasions.

    Now generate the output using the following value for `desc`:

    {desc}
    """


def pipeline_reco_from_wardrobe(new_query, user, infos_text, messages):
    wardrobe, img = generate_wardrobe(new_query, user)
    if img > 0:
        stable_message = {"role": "system", "content": f"Here is the description of the outfit in the image number {img}: {json.dumps(wardrobe['elements'])}"}
    wardrobe = json_to_dataframe(wardrobe, key="elements")
    empty_element = generate_empty_element(new_query)
    content = json.loads(recommend_from_wardrobe((wardrobe, empty_element)))["elements"][0]
    desc = content["description"]
    clothe = fetch_from_img_reco(content)
    reco_message = create_reco_message(clothe, desc)
    messages.append({"role": "user", "content": new_query})
    if img > 0:
        print("Message pour l'image : ", stable_message)
        messages.append(stable_message)
    messages.append({"role": "system", "content": reco_message})
    reco_response = client.chat.complete(
        model="mistral-small-latest",
        messages=messages,
    ).choices[0].message.content
    messages.append({"role": "assistant", "content": reco_response, "dict_infos": clothe})
    return messages, clothe