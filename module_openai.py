import os
import requests  # type: ignore # HTTP requests for downloading images
from openai import OpenAI  # type: ignore # OpenAI SDK client

import model_chat_log  # Local module for chat log management

# Initialize OpenAI client with API key from environment variable
client = OpenAI(api_key=os.environ.get('OPENAI_TOKEN', ''))

# Default AI engine/model to use for chat completions
AI_ENGINE = 'gpt-4o-mini'

# send audio data
def openai_whisper(file_path):
    """
    Transcribe audio file to text using OpenAI Whisper API.
    Args:
        file_path (str): Path to the audio file to transcribe.
    Returns:
        str: Transcribed text or error message.
    """
    ai_response = ''
    try:
        # load audio file to openai
        file = open(file_path, "rb")
        transcription = client.audio.transcriptions.create(
            model="whisper-1", 
            file=file
        )
        print(transcription)
        ai_response = transcription.text
    except Exception as e:
        print(e)
        ai_response = f"OpenAI returns system Error, try your question again: {e}"
        
    print(ai_response)
    return ai_response

# send chat message data
def openai_chat(text, user_id):
    """
    Send a chat message to OpenAI and get a response, maintaining chat history per user.
    Args:
        text (str): User's message.
        user_id (str): Unique identifier for the user (for chat history).
    Returns:
        str: AI's response message.
    """
    # building openai api parameters
    input = model_chat_log.get_logs(user_id=user_id)
    new_message = {"role":"user", "content":text}
    input.append(new_message)

    print(input)

    # send message to openai api
    ai_response = openai_chat_completion(chat=input)

    print(ai_response)

    return ai_response

# generate image by openai
def openai_create_image(prompt, image_path):
    """
    Generate an image using OpenAI's DALL-E API and save it to a file.
    Args:
        prompt (str): Text prompt for image generation.
        image_path (str): Path to save the generated image.
    Returns:
        response_openai: The OpenAI API response object.
    """
    try:
        response_openai = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
        )

        # save image as file
        url = response_openai.data[0].url
        response = requests.get(url)
        with open(image_path, 'wb') as file:
            file.write(response.content)
        return response_openai
    except Exception as e:
        print(f"An error occurred while creating the image: {e}")

# send message to openai api
def openai_chat_completion(chat):
    """
    Send a chat completion request to OpenAI and return the response.
    Args:
        chat (list): List of message dicts for the conversation.
    Returns:
        str: AI's response message or error message.
    """
    ai_response = ''
    try:
        result = client.chat.completions.create(model=AI_ENGINE, messages=chat)
        ai_response = result.choices[0].message.content
    except Exception as e:
        ai_response = f"ChatGPT returns system Error, try your question again: {e}"
    return ai_response

# vision api making image details
def openai_vision(prompt, image_url):
    """
    Use OpenAI Vision API to describe the contents of an image in Japanese, suitable for SNS posts.
    Args:
        prompt (str): Title or context for the image.
        image_url (str): URL of the image to analyze.
    Returns:
        str: Description of the image in Japanese.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"What are in this image? Describe it good for sns post. Return only text of description. The image title tells that {prompt}. Your answer must be Japanese.",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url,
                    },
                },
            ],
            }
        ],
        max_tokens=1000,
    )
    return response.choices[0].message.content
