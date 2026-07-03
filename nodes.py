import requests
import numpy as np
from PIL import Image
from io import BytesIO
import base64
import re
import hashlib
import hmac
import os


class AnyType(str):
    """A socket type that matches any other type during validation."""
    def __ne__(self, other):
        return False


any_type = AnyType("*")


class FlexibleOptionalInputType(dict):
    """Optional-input dict that accepts any dynamically added input name."""
    def __getitem__(self, key):
        return (any_type,)

    def __contains__(self, key):
        return True


class Base64ReadyWebhook:
    def __init__(self):
        pass

    @staticmethod
    def create_hmac_signature(data: bytes, key: bytes, algorithm: str = 'sha256') -> str:
        """
        Creates an HMAC (Keyed-Hash Message Authentication Code) signature for the
        given data using a secret key and the specified algorithm.

        HMAC provides both data integrity and authenticity, as it requires a secret
        key that only the sender and receiver know.

        Args:
            data (bytes): The input data to sign. Must be in bytes.
            key (bytes): The secret key for HMAC. Must be in bytes.
            algorithm (str): The hashing algorithm to use with HMAC (e.g., 'sha256',
                            'sha512'). Defaults to 'sha256'.

        Returns:
            str: The hexadecimal representation of the HMAC signature.
        """
        try:
            # Create an HMAC object
            # The key is crucial for authenticity
            h = hmac.new(key, data, hashlib.sha256)
            # Get the hexadecimal representation of the HMAC
            return h.hexdigest()
        except ValueError:
            return f"Error: Algorithm '{algorithm}' not supported for HMAC."

    @classmethod
    def INPUT_TYPES(s):        
        return {
            "required": {
                "webhook_url": ("STRING", {"default": "webhook_url_goes_here"}),
                "b64ImageData": ("STRING", {"default": "base64_image_string_goes_here"}),
                "post_id": ("STRING", {"default": "post_id_goes_here"}),
                "token": ("STRING", {
                    "default": "tokengoeshere",
                })
            },
            "optional": {
                "message": ("STRING", {
                    "default": "other text goes here",
                }),
            }
        }

    RETURN_TYPES = ("STRING","STRING")
    RETURN_NAMES = ("RESULT", "POST_ID")
    FUNCTION = "on_complete_webhook"
    OUTPUT_NODE = True
    CATEGORY = "spinupart-utils"



    def on_complete_webhook(self, webhook_url, b64ImageData, post_id, token, message):
        print("WEBHOOK HERE")
        print(webhook_url)
        key = os.environ['COMFYSIDE_KEY']
        hash = Base64ReadyWebhook.create_hmac_signature(bytes(b64ImageData, encoding='utf-8'), bytes(key, encoding='utf-8'))
        response = requests.post(webhook_url, json={
            "imageData": b64ImageData,
            "message": message,
            "post_id": post_id,
            "token": token, #main jwt
            "hash": hash
        })

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
            "optional": {
                "quality": ("STRING", { "default": "70" })
            }
        }

    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("Base 64 String", )
    FUNCTION = "image_to_base64"
    OUTPUT_NODE = True
    CATEGORY = "spinupart-utils"

    def image_to_base64(self, images, quality):

        b64string = ''
        for image in images:
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            buffer = BytesIO()
            img.save(buffer, quality=int(quality), format="JPEG")
            b64string = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return {"ui": {"text": b64string}, "result": (b64string, )}  


class RemoveWords:
    def __init__(self):
        pass

    @classmethod

    def INPUT_TYPES(s):        
        return {
            "required": {
                "description": ("STRING", {"default": ""}),
                "removals": ("STRING", {"default": "photo photograph realistic photorealistic"}),
            },
        }

    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("colorless_description", )
    FUNCTION = "remove_words"
    OUTPUT_NODE = True
    CATEGORY = "spinupart-utils"

    def remove_words(self, description, removals):
        """
        Removes common color words from a string, case-insensitively.
        It handles common variations and cleans up extra spaces.
        """
        # A comprehensive list of common color words (you can extend this)
        color_words = removals.split()

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


class StringTemplate:
    """Fills a template string from any number of dynamic inputs.

    Inputs are added on the fly in the UI (INPUT0, INPUT1, ...) and are
    referenced in the template as {{INPUT0}}, {{INPUT1}}, etc. Numeric
    values are converted to text.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "template": ("STRING", {"multiline": True, "default": "{{INPUT0}}"}),
            },
            "optional": FlexibleOptionalInputType(),
        }

    @classmethod
    def VALIDATE_INPUTS(cls, input_types):
        # Dynamic inputs accept any type; skip default type validation.
        return True

    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("string", )
    FUNCTION = "apply_template"
    OUTPUT_NODE = True
    CATEGORY = "spinupart-utils"

    @staticmethod
    def value_to_text(value):
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)

    def apply_template(self, template, **kwargs):
        result = template
        for name, value in kwargs.items():
            result = result.replace("{{" + name + "}}", self.value_to_text(value))
        return {"ui": {"text": [result]}, "result": (result, )}


# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "Base64ReadyWebhook": Base64ReadyWebhook,
    "ImageToBase64": ImageToBase64,
    "RemoveWords": RemoveWords,
    "SpinUpArtStringTemplate": StringTemplate,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
# NOTE: every title starts with "SpinUpArt" so searching "spinupart" in the
# ComfyUI node picker surfaces all nodes from this pack
NODE_DISPLAY_NAME_MAPPINGS = {
    "Base64ReadyWebhook": "SpinUpArt Webhook for Base64 image input",
    "ImageToBase64": "SpinUpArt Convert Image to Base64 string",
    "RemoveWords": "SpinUpArt Remove words from descriptions",
    "SpinUpArtStringTemplate": "SpinUpArt String Template ({{INPUT0}}, {{INPUT1}}, ...)",
}
