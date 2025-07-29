import os
import time
import json

import requests  # type: ignore # HTTP requests for LINE API
from flask import request, Blueprint  # type: ignore # Flask request object and Blueprint for modular routing
from linebot import LineBotApi  # type: ignore # LINE SDK

import model_chat_log  # Chat log management
import module_openai  # OpenAI API integration
import module_gcp_storage  # Google Cloud Storage integration
import module_stability  # Stability AI image generation
import module_enhanced_image  # Enhanced image generation
import prompt_templates  # Prompt templates and help
import prompt_config  # Prompt validation

LINE_API_TOKEN = os.environ.get('LINE_API_TOKEN', '')

# Create a Flask Blueprint for LINE webhook handling
line_app = Blueprint('handle_line', __name__)

def _handle_image_generation(text: str, user_id: str, current_time_string: str, command: str) -> tuple[str, str]:
    """
    Handle image generation with enhanced prompts.
    
    Args:
        text: User's input text
        user_id: User ID for file naming
        current_time_string: Timestamp string
        command: Command to remove from text
        
    Returns:
        Tuple of (response_text, image_url)
    """
    image_path = f"/tmp/image_{user_id}.png"
    user_prompt = text.replace(command, "").strip()
    
    # Validate prompt
    is_valid, validation_message = prompt_config.validate_prompt(user_prompt)
    if not is_valid:
        return validation_message, ""
    
    # Determine provider based on command
    provider_map = {
        "genimg": "openai",
        "genimgsd": "stability", 
        "genauto": "auto",
        "genanime": "stability",
        "genphoto": "openai",
        "genrandom": "auto"
    }
    provider = provider_map.get(command, "auto")
    
    try:
        if command == "genanime":
            result = module_enhanced_image.enhanced_generator.generate_anime_character(
                user_prompt, image_path=image_path
            )
        elif command == "genphoto":
            result = module_enhanced_image.enhanced_generator.generate_photorealistic(
                user_prompt, image_path=image_path
            )
        elif command == "genrandom":
            subject = user_prompt if user_prompt else None
            result = module_enhanced_image.enhanced_generator.generate_random_artwork(
                subject, image_path=image_path
            )
        else:
            result = module_enhanced_image.enhanced_generator.generate_with_enhanced_prompt(
                user_prompt, provider=provider, image_path=image_path
            )
        
        if result['success']:
            image_url = module_gcp_storage.upload_to_bucket(current_time_string, image_path, "ai-bot-app")
            print(f"Generated with {result['provider']}: {result['enhanced_prompt']}")
            return "", image_url
        else:
            return f"Image generation failed: {result['error']}", ""
            
    except Exception as e:
        return f"System Error: {str(e)}", ""

@line_app.route("/openai_gpt_line", methods=["POST"])
def openai_gpt_line():
    """
    Webhook endpoint for LINE messaging API. Handles incoming messages, processes text/audio,
    generates responses or images using AI APIs, manages chat logs, and replies to users.
    """
    # Extract line message event parameters
    request_json = request.json
    print(request_json)
    events = request_json["events"]
    event = events[0]
    replyToken = event["replyToken"]
    type = event["message"]["type"]
    user_id = event["source"]["userId"]
    message_id = event["message"]["id"]

    response_text = ""
    image_url = ""

    current_time = int(time.time())
    current_time_string = str(current_time)
    
    if "audio" in type:
        # Use line sdk library to get audio file
        line_bot_api = LineBotApi(LINE_API_TOKEN)
        message_content = line_bot_api.get_message_content(message_id)
        file_path = f"/tmp/{user_id}.m4a"
        with open(file_path, 'wb') as fd:
            for chunk in message_content.iter_content():
                fd.write(chunk)

        # Trans voice data to text
        trans_text = module_openai.openai_whisper(file_path)
        ai_text = module_openai.openai_chat(text=trans_text, user_id=user_id)
        response_text = f"Q:{trans_text}\nA:{ai_text}"

        # Save chat logs
        model_chat_log.save_log(user_id=user_id, role="user", message=trans_text)
        model_chat_log.save_log(user_id=user_id, role="assistant", message=ai_text)
    else:
        text = event["message"]["text"]
        
        # Handle different commands
        if "reset" in text:
            model_chat_log.delete_logs(user_id=user_id)
            response_text = "reset chat logs!"
        elif "help" in text.lower() or "image help" in text.lower():
            response_text = prompt_templates.USAGE_INSTRUCTIONS
        elif any(cmd in text for cmd in ["genimg", "genimgsd", "genauto", "genanime", "genphoto", "genrandom"]):
            # Find which command was used
            commands = ["genimg", "genimgsd", "genauto", "genanime", "genphoto", "genrandom"]
            used_command = next((cmd for cmd in commands if cmd in text), None)
            
            if used_command:
                response_text, image_url = _handle_image_generation(
                    text, user_id, current_time_string, used_command
                )
        elif "text" in type:
            response_text = module_openai.openai_chat(text, user_id=user_id)
            
            # Save chat logs
            model_chat_log.save_log(user_id=user_id, role="user", message=text)
            model_chat_log.save_log(user_id=user_id, role="assistant", message=response_text)

    print(replyToken)
    print(response_text)

    # Extract ai response and reply to line
    message = {}
    if response_text != "":
        message = {"type": "text", "text": response_text}
    elif image_url != "":
        message = {"type": "image", "originalContentUrl": image_url, "previewImageUrl": image_url}

    messages = [message]
    data = {"replyToken": replyToken, "messages": messages}
    headers = {'content-type': 'application/json', 'Authorization': f'Bearer {LINE_API_TOKEN}'}
    res = requests.post("https://api.line.me/v2/bot/message/reply", data=json.dumps(data), headers=headers)
    print(res.json())

    return "ok"
