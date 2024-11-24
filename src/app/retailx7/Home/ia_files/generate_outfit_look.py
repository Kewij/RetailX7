from datetime import datetime
import urllib.request
import base64
import json
import time
import os

webui_server_url = 'http://127.0.0.1:7860'

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
    data = json.dumps(payload).encode('utf-8')
    request = urllib.request.Request(
        f'{webui_server_url}/{api_endpoint}',
        headers={'Content-Type': 'application/json'},
        data=data,
    )
    response = urllib.request.urlopen(request)
    return json.loads(response.read().decode('utf-8'))


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

        # Parameters for Refiner and ControlNet
        "alwayson_scripts": {
            "ControlNet": {
                 "args": [
                     {
                         "batch_images": "",
                         "control_mode": "Balanced",
                         "enabled": True,
                         "guidance_end": 1,
                         "guidance_start": 0,
                         "image": {
                             "image": encode_file_to_base64(path_to_ref_picture),
                             "mask": None  # base64, None when not need
                         },
                         "input_mode": "simple",
                         "is_ui": True,
                         "loopback": False,
                         "low_vram": False,
                         "model": "control_v11p_sd15_canny [d14c016b]",
                         "module": "canny",
                         "output_dir": "",
                         "pixel_perfect": False,
                         "processor_res": 512,
                         "resize_mode": "Crop and Resize",
                         "threshold_a": 100,
                         "threshold_b": 200,
                         "weight": 1
                     }
                 ]
            },
            "Refiner": {
                "args": [
                    True,
                    "sd_xl_refiner_1.0",
                    0.5
                ]
            },
            "Adetailer": {
                "args": [
                    True,
                    "face_yolov8n.pt"
                ]
            }
        },

        # Choose the model chekcpoint (could be specified in the bat file of the auto)
        "override_settings": {
            # "sd_model_checkpoint": "v1-5-pruned-emaonly.safetensors [6ce0161689]",
            #"sd_model_checkpoint": "IPXL_v8.safetensors [6bd1a90a93]",
            "sd_model_checkpoint": "cyberrealistic_v40.safetensors [481d75ae9d]", 
        },
    }
    call_txt2img_api(**payload)
