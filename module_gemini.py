"""
This module provides functions to interact with Google's Gemini and Imagen AI APIs for chat and image generation.
- Requires: google-generativeai, Pillow, and related dependencies.
"""

import os
import base64
from io import BytesIO

from PIL import Image  # type: ignore # Image processing
import model_chat_log  # Local module for chat log management
import google.generativeai as google_genai  # type: ignore # Google Gemini API
from google import genai  # Google GenAI client
from google.genai import types  # type: ignore # Google GenAI types

# Configure Gemini API key from environment variable
google_genai.configure(api_key=os.environ.get('GEMINI_TOKEN', ''))

# Set up the model configuration for Gemini
# Controls randomness, output length, and safety settings
generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

model = google_genai.GenerativeModel(model_name="gemini-2.5-flash-preview-05-20",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

# send chat message data
def gemini_chat(text, user_id):
    """
    Send a chat message to Gemini, maintaining chat history per user.
    Args:
        text (str): User's message.
        user_id (str): Unique identifier for the user (for chat history).
    Returns:
        str: AI's response message or error message.
    """
    try:
      # get chat history from database
      history = model_chat_log.get_logs_gemini(user_id=user_id)
      print(history)
      # send prompt and extract result
      convo = model.start_chat(history=history)
      convo.send_message(text)
      print(convo.last.text)
      return convo.last.text
    except Exception as e:
        print(e)
        return f"Gemini returns system Error, try your question again: {e}"

# generate image by Imagen
def exec_imagen(prompt, image_path):
    """
    Generate an image using Google's Imagen API and save it to a file.
    Args:
        prompt (str): Text prompt for image generation.
        image_path (str): Path to save the generated image.
    Returns:
        None. Saves the image to the specified path.
    """
    # Generate image using Imagen (Google)
    client = genai.Client(api_key=os.environ.get("GEMINI_TOKEN"))
    result = client.models.generate_images(
        model="models/imagen-4.0-generate-001",
        prompt=prompt,
        config=dict(
            number_of_images=1,
            output_mime_type="image/jpeg",
            person_generation="ALLOW_ADULT",
            aspect_ratio="1:1",
        ),
    )

    if result.generated_images:
      image_data = result.generated_images[0].image.image_bytes
      img = Image.open(BytesIO(image_data))
      img.save(image_path)

# chat with image and text input
def gemini_chat_with_image(image_path, prompt_text):
    """
    Send an image and text prompt to Gemini for multimodal chat.
    Args:
        image_path (str): Path to the image file.
        prompt_text (str): Text prompt to send with the image.
    Returns:
        str: AI's response message or error message.
    """
    try:
        with open(image_path, "rb") as img_file:
            image_bytes = img_file.read()
        encoded_image = base64.b64encode(image_bytes)

        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_bytes(mime_type="image/jpeg", data=base64.b64decode(encoded_image)),
                    types.Part.from_text(text=prompt_text)
                ],
            )
        ]

        generate_content_config = types.GenerateContentConfig(response_mime_type="text/plain")

        genai_client = genai.Client(api_key=os.environ.get("GEMINI_TOKEN"))
        # Generate content with image and text
        response = ""
        for chunk in genai_client.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=contents,
            config=generate_content_config,
        ):
            response += chunk.text or ""
        return response

    except Exception as e:
        print(f"Error during image + text Gemini request: {e}")
        return f"Error: {e}"
