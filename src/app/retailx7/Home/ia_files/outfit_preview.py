import requests
import base64

# Define the URL and the payload to send.
url = "http://127.0.0.1:9090"

def generate_outfit_preview(prompt, negative_prompt):
    payload = {
            
            "prompt": prompt,  # extra networks also in prompts
            "negative_prompt": negative_prompt,
            "seed": 1,
            "steps": 20,
            "width": 512,
            "height": 512,
            "cfg_scale": 7,
            "sampler_name": "DPM++ 2M Karras",
            "n_iter": 1,
            "batch_size": 1,
            "override_settings": {
                "sd_model_checkpoint": "realisticVisionV60B1_v51HyperVAE.safetensors [f47e942ad4]", 
            },

            
        }

    # Send said payload to said URL through the API.
    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
    r = response.json()

    # Decode and save the image.
    with open("output.png", 'wb') as f:
        f.write(base64.b64decode(r['images'][0]))