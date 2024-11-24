
from .outfit_preview import generate_outfit_preview
import os
from mistralai import Mistral
from Home.models import ImageGenere

model = "mistral-small-latest"
api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)


def callback_generate_outfit_preview(prompt):
    positive_prompt = add_prompt_for_stable_diff(prompt)
    negative_prompte = "((((ugly)))), (((duplicate))), ((morbid)), ((mutilated)), [out of frame], extra fingers, mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), ((ugly)), blurry, ((bad anatomy)), (((bad proportions))), ((extra limbs)), cloned face, (((disfigured))), out of frame, ugly, extra limbs, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), (((extra arms))), (((extra legs))), mutated hands, (fused fingers), (too many fingers), (((long neck)))"
    image = generate_outfit_preview(positive_prompt, negative_prompte)
    return image

def is_generate_outfit(user_input):
    prompt = "Analyze the user's input and determine if they are explicitly requesting outfit generation. Respond with either True or False, based solely on whether the user’s input suggests they want to genrate an outfit. Do not include any punctuation in your response."
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



def make_prompt_stable_diff(user_input, infos_text=None):
    if infos_text == None:
        return f"""
        Based on your last propositions, and on what the user desired, provide a brief and impactful descrition. Give only the description without commentaries.

        # Example Conversation:
        User Input:
        "Can i see a preview of the outfit."
        #

        # User Input:
        {user_input}
        """
    else:
        return f"""
        Based on your last propositions, and on what the user desired, provide a brief and impactful descrition. Give only the description without commentaries.
        # Example Conversation:
        User Input:
        "What would this sweater looklike with my previous outfits."
        #

        This is my outfits' description:
        {infos_text}

        # User Input:
        {user_input}
        """
    
def add_prompt_for_stable_diff(prompt):
    return "High quality realistic photo of a man wearing " + prompt 

def pipeline_preview_outfit(user_input, infos_text=None, messages=[]):
    # Met le prompt dans le LLM
    # messages.append({"role":"user", "content":prompt})
    prompt = make_prompt_stable_diff(user_input, infos_text)
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
    image = callback_generate_outfit_preview(queries)
    image_instance = ImageGenere.objects.create(image=image)
    image_url = image_instance.image.url
    messages.append({"role": "assistant", "content": "This the preview", "dict_infos" : [{"imageUrl" : image_url}]})
    
    return messages
