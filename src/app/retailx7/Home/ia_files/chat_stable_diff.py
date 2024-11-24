
from .outfit_preview import generate_outfit_preview
import os
from mistralai import Mistral
from Home.models import ImageGenere

from django.core.files.base import ContentFile

model = "mistral-small-latest"
api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)


def callback_generate_outfit_preview(prompt, infos_text=None):
    positive_prompt = add_prompt_for_stable_diff(prompt, infos_text)
    negative_prompte = "((((ugly)))), (((duplicate))), ((morbid)), ((mutilated)), [out of frame], extra fingers, mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), ((ugly)), blurry, ((bad anatomy)), (((bad proportions))), ((extra limbs)), cloned face, (((disfigured))), out of frame, ugly, extra limbs, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), (((extra arms))), (((extra legs))), mutated hands, (fused fingers), (too many fingers), (((long neck)))"
    image = generate_outfit_preview(positive_prompt, negative_prompte)
    return image

def is_generate_outfit(user_input):
    prompt = "Analyze the user's input and determine if they are explicitly requesting a preview of an outfit. Respond with either True or False, based solely on whether the user’s input suggests they want to genrate an outfit. Do not include any punctuation in your response."
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
    return """
        Based on your last propositions, and on what the user desired, provide a brief and impactful descrition. Give only the description without commentaries.
        # Example Conversation:
        System answers:
        "{"elements": [
        {
            "element": "Oversized Sweatshirt",
            "color": "Light Beige",
            "fit": "Loose and relaxed, with dropped shoulders and a cropped hem.",
            "price": "Estimated $50-$70",
            "context": "Casual, everyday wear",
            "description": "A light beige oversized sweatshirt with the number '1965' emblazoned across the front, offering a casual and laid-back vibe perfect for everyday wear."
        },
        {
            "element": "Distressed Jeans",
            "color": "Dark Blue",
            "fit": "Baggy and oversized, with distressed details and rips.",
            "price": "Estimated $70-$90",
            "context": "Casual, streetwear",
            "description": "Dark blue distressed jeans with intentional rips and a baggy fit, adding a rugged and edgy touch to the outfit, ideal for a streetwear look."
        },}"

        LLM answers:
        "I’ve found a recommendation that matches your request. A beige dad cap with a subtle logo to match image number 6. This accessory adds an understated, modern touch to the outfit, complementing the oversized hoodie and distressed jeans. The beige color contributes to the monochromatic theme, creating a cohesive and harmonious look while maintaining the casual streetwear vibe. The slight curve on the brim provides a relaxed, laid-back feel, perfect for everyday wear."

        User Input:
        "What would this looklike ?"
        

        LLM answers:
        "A beige dad cap, beige oversized sweatshirt, distressed dark blue jeans"

        #

        # User Input:
        %s
        """ % user_input
    
def add_prompt_for_stable_diff(prompt, infos_text=None):
    print(infos_text)
    if infos_text == None:
        return "High quality realistic photo of a man wearing " + prompt
    return  f"High quality realistic photo of a {infos_text["gender"]} wearing " + prompt

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
    image_data = callback_generate_outfit_preview(queries, infos_text)
    image_file = ContentFile(image_data, name="generated_image.png") 
    image_instance = ImageGenere.objects.create(image=image_file)
    image_url = "devops.tlapp.net" + image_instance.image.url
    messages.append({"role":"user", "content":user_input})
    messages.append({"role": "assistant", "content": "This the preview", "dict_infos" : [{"imageUrl" : image_url}]})
    
    return messages
