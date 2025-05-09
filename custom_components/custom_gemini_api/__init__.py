#imports
import base64
import requests
import json

from homeassistant.core import SupportsResponse

DOMAIN = 'gemini_api'

CONF_API_KEY = 'api_key'

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key="

def setup(hass, config):
    """Service to send prompt and images to gemini."""
    api_key = config[DOMAIN][CONF_API_KEY]
    gemini_full_url = GEMINI_URL + api_key

    def generate_text(call):
        text = ""
        try:
            prompt = call.data.get('prompt')
            images = call.data.get('images')

            if images:
                image_base64 = [base64.b64encode(open(image, "rb").read()).decode('utf-8') for image in images]
            else:
                image_base64 = []

            parts = [{"text": prompt}]
            if images:
                for image_base64 in image_base64:
                    parts.append({
                        "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": image_base64
                        }
                    })

            content = {
                "contents": [{
                "parts": parts
                }]
            }

            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.post(gemini_full_url, headers=headers, data=json.dumps(content))

            text = ""
            if response.status_code == 200:
                text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            else:
                text = f"Error {response.status_code}: {response.text}"

        except Exception as e:
            text = f"Exception {e.message}"

        return {
            "text": text
        }

    hass.services.register(DOMAIN, 'generate_text', generate_text, supports_response=SupportsResponse.ONLY)
    return True
