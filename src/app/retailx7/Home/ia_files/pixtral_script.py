import os
import base64
from mistralai import Mistral
import json
import pandas as pd
from typing import Union

# Load Mistral API key from environment variables
api_key = os.environ["MISTRAL_API_KEY"]

# Model specification
model = "mistral-large-latest"

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