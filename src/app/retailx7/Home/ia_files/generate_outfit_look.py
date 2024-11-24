from datetime import datetime
import urllib.request
import base64
import json
import time
import os

webui_server_url = 'http://localhost:9090'

out_dir = 'api_out'
out_dir_t2i = os.path.join(out_dir, 'txt2img')
out_dir_i2i = os.path.join(out_dir, 'img2img')
os.makedirs(out_dir_t2i, exist_ok=True)
os.makedirs(out_dir_i2i, exist_ok=True)



def timestamp():
    return datetime.fromtimestamp(time.time()).strftime("%Y%m%d-%H%M%S")


def encode_file_to_base64(path):
    with open(path, 'rb') as file:
        return base64.b64encode(file.read()).decode('utf-8')


def decode_and_save_base64(base64_str, save_path):
    with open(save_path, "wb") as file:
        file.write(base64.b64decode(base64_str))


def call_api(api_endpoint, **payload):
    # Convert the payload to JSON
    data = json.dumps(payload).encode('utf-8')

    # Construct the full URL
    url = f'{webui_server_url}/{api_endpoint}'

    # Create the request
    request = urllib.request.Request(
        url,
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json'  # Add Accept header for APIs expecting it
        },
        data=data,
        method='POST'  # Explicitly define the method
    )

    # Send the request and handle errors
    try:
        with urllib.request.urlopen(request) as response:
            # Parse and return the response JSON
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"HTTPError: {e.code} {e.reason}")
        print(f"Response: {e.read().decode('utf-8')}")
        raise
    except urllib.error.URLError as e:
        print(f"URLError: {e.reason}")
        raise



def call_txt2img_api(**payload):
    response = call_api('sdapi/v1/txt2img', **payload)
    for index, image in enumerate(response.get('images')):
        save_path = os.path.join(out_dir_t2i, f'txt2img-{timestamp()}-{index}.png')
        decode_and_save_base64(image, save_path)


def call_img2img_api(**payload):
    response = call_api('sdapi/v1/img2img', **payload)
    for index, image in enumerate(response.get('images')):
        save_path = os.path.join(out_dir_i2i, f'img2img-{timestamp()}-{index}.png')
        decode_and_save_base64(image, save_path)


def generate_outfit_preview(prompt, negative_prompt, path_to_ref_picture):
    """Use the API from stable diffusion to generate the preview of the outfit using
    Inputs:
     - prompt : the prompt for the generated image (String)
     - negative_prompt : what the generated image should avoid looking like (String)
     - path_to_ref_picutre : the path to the picture the outline will be matched to (String)
    Outputzs:
     - Save the generated image
    """
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

        
    }
    call_txt2img_api(**payload)
