import base64
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# encode the image from byte to string because the API expects images as URLs or encoded strings
def encode_image(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


def detect_image_mime_type(image_bytes: bytes) -> str:
    # Detect supported formats from magic bytes and fail fast otherwise.
    if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if image_bytes.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    raise ValueError("Unsupported image format. Please upload a JPG, JPEG, or PNG image.")

# main function for image detection
# input: image
# output: list of ingredients 
def detect_ingredients(image_bytes: bytes) -> list[str]:
    
    base64_image = encode_image(image_bytes)
    image_mime_type = detect_image_mime_type(image_bytes)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role" : "user", 
                "content" : [
                    {
                        "type" : "image_url",
                        "image_url" : {
                            "url" : f"data:{image_mime_type};base64,{base64_image}"
                        }
                    },
                    {
                        "type" : "text", 
                        "text" : (
                            "Look at this image carefully. "
                            "List every ingredients you can see. "
                            "Return ONLY the comma-separated list of ingredient names (all lowercase), nothing else. "
                            "Example format: eggs, tomatos, spinach, cheese . "
                            "If you cannot detect any food, return the word: none ."
                        )
                    }
                ]
            }
        ],
        max_tokens=300
    )

    raw = response.choices[0].message.content.strip() # remove white space of the list

    if raw == "none":
        return []
    
    ingredients = [i.strip().lower() for i in raw.split(",")] # strips whitespace, lowercases everything of individual ingredients

    return [i for i in ingredients if i] # removes any empty strings




