from apify_client import ApifyClient
import matplotlib.pyplot as plt
from skimage import io
import ast

import os
from mistralai import Mistral
import json
import functools

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
    outfit = {}
    for i, query in enumerate(queries):
        clothe = scrap_asos(query, maxItems)
        outfit[query] = clothe
    return outfit

def create_first_message(outfit):
    return f"""
    Here are your recommandations :
    {outfit}
    Summarize the different items mentioned by the user in the form of bullet points. 
    Each bullet point must include relevant details about the respective item.

    # Example of response:
    'Introduction to the response'
    - Lightweight denim jacket
        - relevant details
    - Relaxed-fit cotton T-shirt
        - relevant details
    - Slim-fit joggers
        - relevant details
    - White sneakers
        - relevant details
    """

def pipeline_chatbot(user_input, messages=[]):
    # Met le prompt dans le LLM
    # messages.append({"role":"user", "content":prompt})
    prompt = make_prompt(user_input)
    chat_response = client.chat.complete(
        model=model,
        messages=[{"role":"user", "content":prompt}]
    )
    # Récupère et process les outfits donnés par le LLM
    queries = chat_response.choices[0].message.content
    print(queries)
    outfit = scrap_asos_outfit(queries, maxItems=1)
    outfit = {query: [{k: v for k, v in item.items() if k != "image"} for item in clothe] for query, clothe in outfit.items()}
    # Créé et envoie un message à envoyer au user
    message_outfit = create_first_message(json.dumps(outfit, indent=4))
    print(message_outfit)
    messages.append({"role":"system", "content":message_outfit})
    chat_response = client.chat.complete(
        model = model,
        messages = messages
    )
    messages.pop()
    messages.append({"role": "user", "content": user_input})
    messages.append({"role": "assistant", "content": chat_response.choices[0].message.content, "dict_infos" : {}})
    
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
