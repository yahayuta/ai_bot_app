"""
At the command line, only need to run once to install the package via pip:

$ pip install google-generativeai
"""

import os
import base64
from io import BytesIO
from PIL import Image  # type: ignore
import model_chat_log
import google.generativeai as google_genai  # type: ignore
from google import genai
from google.genai import types # type: ignore

google_genai.configure(api_key=os.environ.get('GEMINI_TOKEN', ''))

# Set up the model
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
    # Generate image using Imagen (Google)
    client = genai.Client(api_key=os.environ.get("GEMINI_TOKEN"))
    result = client.models.generate_images(
        model="models/imagen-3.0-generate-002",
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
            model="gemini-2.5-flash-preview-05-20",
            contents=contents,
            config=generate_content_config,
        ):
            response += chunk.text or ""
        return response

    except Exception as e:
        print(f"Error during image + text Gemini request: {e}")
        return f"Error: {e}"
