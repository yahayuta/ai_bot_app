import os
import requests # type: ignore
import json
import facebook # type: ignore
import random
import time
import model_chat_log
import module_openai
import module_stability
import module_common
import module_gemini

from flask import request # type: ignore
from flask import Blueprint # type: ignore

FACEBOOK_PAGE_ACCESS_TOKEN =  os.environ.get('FACEBOOK_PAGE_ACCESS_TOKEN', '')
FACEBOOK_PAGE_VERIFY_TOKEN =  os.environ.get('FACEBOOK_PAGE_VERIFY_TOKEN', '')
FACEBOOK_PAGE_ID = os.environ.get('FACEBOOK_PAGE_ID', '')

facebook_app = Blueprint('handle_facebook', __name__)

@facebook_app.route("/openai_gpt_facebook_autopost_news")
def openai_gpt_facebook_autopost_news():

    url = "https://news.google.com/rss"
    response = requests.get(url)
    # Get the response content as a string
    result = response.text
    text = f'summarize in japanese following:{result}'
    new_message = {"role":"user", "content":text}
    input = []
    input.append(new_message)

    # send message to openai api
    ai_response = module_openai.openai_chat_completion(chat=input)
    print(ai_response)

    # Initialize a Facebook Graph API object
    graph = facebook.GraphAPI(FACEBOOK_PAGE_ACCESS_TOKEN)

    news_sum = f"最新ニューストピック：\n{ai_response}"
    # Make a post to the Facebook page
    graph.put_object(
        parent_object=FACEBOOK_PAGE_ID,
        connection_name='feed',
        message=news_sum
    )

    return "ok", 200

@facebook_app.route("/openai_gpt_facebook_autopost_image")
def openai_gpt_facebook_autopost_image():

    # pick topic randomly
    picked_topic = random.choice(module_common.topic)
    picked_place = random.choice(module_common.place)

    # make openai parameter
    input = []
    text = f'pick one {picked_topic} in {picked_place} countries then talk about it very shortly'
    new_message = {"role":"user", "content":text}
    input.append(new_message)

    # send message to openai api
    prompt = module_openai.openai_chat_completion(chat=input)
    print(prompt)

    # generate image by openai
    image_path = f"/tmp/image_{FACEBOOK_PAGE_ID}.png"
    module_openai.openai_create_image(prompt, image_path)
    
    # gemini chat with image and text input
    ai_response = module_gemini.gemini_chat_with_image(image_path, get_chat_with_image_template(prompt))

    # Initialize a Facebook Graph API object
    graph = facebook.GraphAPI(FACEBOOK_PAGE_ACCESS_TOKEN)

    # Open the image file to be uploaded
    with open(image_path, 'rb') as image:
        # Upload the image to Facebook and get its ID
        graph.put_photo(image, album_id=FACEBOOK_PAGE_ID, caption=ai_response)

    return "ok", 200

@facebook_app.route("/stability_facebook_autopost_image")
def stability_facebook_autopost_image():

    # pick topic randomly
    cartoon = random.choice(module_common.cartoons)
    pattern = random.choice(module_common.patterns)

    prompt = f"{cartoon}, {pattern}"

    print(prompt)

    # generate image by stability
    current_time = int(time.time())
    current_time_string = str(current_time)
    image_path = f"/tmp/image_stability_{current_time_string}.png"
    module_stability.generate(prompt, image_path)

    # gemini chat with image and text input
    ai_response = module_gemini.gemini_chat_with_image(image_path, get_chat_with_image_template(prompt))

    print(ai_response)

    # Initialize a Facebook Graph API object
    graph = facebook.GraphAPI(FACEBOOK_PAGE_ACCESS_TOKEN)

    # Open the image file to be uploaded
    with open(image_path, 'rb') as image:
        # Upload the image to Facebook and get its ID
        graph.put_photo(image, album_id=FACEBOOK_PAGE_ID, caption=ai_response)

    return "ok", 200

@facebook_app.route("/gemini_facebook_autopost_image")
def gemini_facebook_autopost_image():

    # pick topic randomly
    cartoon = random.choice(module_common.cartoons)
    pattern = random.choice(module_common.patterns)

    prompt = f"{cartoon}, {pattern}"

    print(prompt)

    # generate image by stability
    current_time = int(time.time())
    current_time_string = str(current_time)
    image_path = f"/tmp/image_gemini_{current_time_string}.png"
    module_gemini.exec_imagen(prompt, image_path)

    # gemini chat with image and text input
    ai_response = module_gemini.gemini_chat_with_image(image_path, get_chat_with_image_template(prompt))

    print(ai_response)

    # Initialize a Facebook Graph API object
    graph = facebook.GraphAPI(FACEBOOK_PAGE_ACCESS_TOKEN)

    # Open the image file to be uploaded
    with open(image_path, 'rb') as image:
        # Upload the image to Facebook and get its ID
        graph.put_photo(image, album_id=FACEBOOK_PAGE_ID, caption=ai_response)

    return "ok", 200

@facebook_app.route('/openai_gpt_facebook', methods=['GET'])
def openai_gpt_facebook_verify():
    # Facebook requires a challenge token to verify the webhook
    challenge = request.args.get('hub.challenge')
    if FACEBOOK_PAGE_VERIFY_TOKEN == request.args.get('hub.verify_token'):
        return challenge
    else:
        return "Invalid verification token"

@facebook_app.route('/openai_gpt_facebook', methods=['POST'])
def openai_gpt_facebook_webhook():
    # print(request.headers)
    data = request.get_json()
    print(data)
    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                # Check if the message is a text message
                if messaging_event.get('message') and 'text' in messaging_event['message']:
                    sender_id = messaging_event['sender']['id']
                    message_text = messaging_event['message']['text']
                    handle_message_facebook(message_text, sender_id)
    print("finish request")
    return "ok", 200

# handle facebook message by webhook
def handle_message_facebook(message_text, sender_id):
    print(message_text)
    reply_text = ""
    # send message to openai
    if "reset" in message_text:
        model_chat_log.delete_logs(user_id=sender_id)
        reply_text = "reset chat logs!"
    else:
        reply_text = module_gemini.gemini_chat(text=message_text, user_id=sender_id)
        # save chat logs with ai
        model_chat_log.save_log(user_id=sender_id, role="user", message=message_text)
        model_chat_log.save_log(user_id=sender_id, role="model", message=reply_text)

    print(reply_text)
    send_message(sender_id, reply_text)

# send message by facebook api
def send_message(recipient_id, message_text):
    params = {
        "access_token": FACEBOOK_PAGE_ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v12.0/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        print(r.status_code)
        print(r.text)

# This function returns a template for the chat with image prompt
def get_chat_with_image_template(prompt):
    return f"What are in this image? Describe it good for sns post. Return only text of description. The image title tells that {prompt}. Your answer must be Japanese."
