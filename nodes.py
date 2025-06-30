import requests
import numpy as np
from PIL import Image
from io import BytesIO
import base64
import re


class Base64ReadyWebhook:
    
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):        
        return {
            "required": {
                "webhook_url": ("STRING", {"default": "webhook_url_goes_here"}),
                "b64ImageData": ("STRING", {"default": "base64_image_string_goes_here"}),
                "post_id": ("STRING", {"default": "post_id_goes_here"})
            },
            "optional": {
                "message": ("STRING", {
                    "default": "other text goes here",
                })
            }
        }

    RETURN_TYPES = ("STRING","STRING")
    RETURN_NAMES = ("RESULT", "POST_ID")
    FUNCTION = "on_complete_webhook"
    OUTPUT_NODE = True
    CATEGORY = "spinupart-utils"

    def on_complete_webhook(self, webhook_url, b64ImageData, post_id, message):


        response = requests.post(webhook_url, json={"imageData": b64ImageData, "message": message, "post_id": post_id})

        return (response.text, post_id)  


class ImageToBase64:
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):        
        return {
            "required": {
                "images": ("IMAGE", ),
            },
        }

    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("Base 64 String", )
    FUNCTION = "image_to_base64"
    OUTPUT_NODE = True
    CATEGORY = "spinupart-utils"

    def image_to_base64(self, images):

        b64string = ''
        for image in images:
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            buffer = BytesIO()
            img.save(buffer, quality=70, format="JPEG")
            b64string = base64.b64encode(buffer.getvalue()).decode('utf-8')

            print(b64string)

        return {"ui": {"text": b64string}, "result": (b64string, )}  


class RemoveColorWords:
    def __init__(self):
        pass

    @classmethod

    def INPUT_TYPES(s):        
        return {
            "required": {
                "description": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("colorless_description", )
    FUNCTION = "remove_color_words"
    OUTPUT_NODE = True
    CATEGORY = "spinupart-utils"

    def remove_color_words(self, description):
        """
        Removes common color words from a string, case-insensitively.
        It handles common variations and cleans up extra spaces.
        """
        # A comprehensive list of common color words (you can extend this)
        color_words = [
            "red", "blue", "green", "yellow", "orange", "purple", "pink", "black",
            "white", "gray", "grey", "brown", "gold", "silver", "cyan", "magenta",
            "teal", "maroon", "navy", "olive", "lime", "aqua", "fuchsia", "indigo",
            "violet", "beige", "turquoise", "lavender", "plum", "salmon", "khaki",
            "peach", "coral", "crimson", "chartreuse", "ivory", "tan", "bronze",
            "periwinkle", "saffron", "emerald", "ruby", "jade", "topaz", "pearl",
            "mustard", "charcoal", "photo", "photograph"
        ]

        # Create a regex pattern to match any of the color words as whole words
        # sorted by length descending to match longer words first (e.g., "light blue" before "blue")
        # Using r'\b' for word boundaries and re.IGNORECASE for case-insensitivity
        pattern = r'\b(?:' + '|'.join(re.escape(word) for word in sorted(color_words, key=len, reverse=True)) + r')\b'

        values = []

        # Replace the color words with an empty string
        cleaned_text = re.sub(pattern, '', description, flags=re.IGNORECASE)

        # Clean up any extra spaces that might result from the removal
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

        values.append(cleaned_text)
        return {"ui": {"text": values }, "result": (cleaned_text, )}



# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "Base64ReadyWebhook": Base64ReadyWebhook,
    "ImageToBase64": ImageToBase64,
    "RemoveColorWords": RemoveColorWords
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "Base64ReadyWebhook": "Webhook for Base64 image input",
    "ImageToBase64": "Convert Image to Base64 string",
    "RemoveColorWords": "Removes all references to color from BLIP and related descriptions"
}
