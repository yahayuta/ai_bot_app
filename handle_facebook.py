import os
import requests
import json
import threading
import facebook
import random
import model_openai_chat_log
import base64
import module_openai

from flask import request
from flask import Blueprint
from newsapi import NewsApiClient
from googletrans import Translator

FACEBOOK_PAGE_ACCESS_TOKEN =  os.environ.get('FACEBOOK_PAGE_ACCESS_TOKEN', '')
FACEBOOK_PAGE_VERIFY_TOKEN =  os.environ.get('FACEBOOK_PAGE_VERIFY_TOKEN', '')
FACEBOOK_PAGE_ID = os.environ.get('FACEBOOK_PAGE_ID', '')
NEWS_API_KEY = os.environ.get('NEWS_API_KEY', '')

facebook_app = Blueprint('handle_facebook', __name__)

topic = [
   "musician or group or band",
   "movie",
   "drama",
   "place",
   "politician",
   "athlete",
   "comedian",
   "actor",
   "actress",
   "city"
]

place = [
    "North America",
    "South America",
    "Asia",
    "Europe",
    "Africa",
    "Oceania"
]

@facebook_app.route("/openai_gpt_facebook_autopost_news")
def openai_gpt_facebook_autopost_news():

    # initialize NewsApiClient with your API key
    newsapi = NewsApiClient(api_key=NEWS_API_KEY)

    # get top headlines in Japan in Japanese language
    top_headlines = newsapi.get_top_headlines(country='us')

    news = ""
    # print each article's title and description
    for idx, article in enumerate(top_headlines['articles']):
        if article['description'] is not None:
            news += f"\n{idx + 1}.{article['description']}"

    # make openai parameter
    input = []
    text = f'translate to japanese following:{news}'
    print(text)
    new_message = {"role":"user", "content":text}
    input.append(new_message)

    # send message to openai api
    ai_response = module_openai.openai_chat_completion(chat=input)
    print(ai_response)

    # Initialize a Facebook Graph API object
    graph = facebook.GraphAPI(FACEBOOK_PAGE_ACCESS_TOKEN)

    news_sum = f"アメリカ最新ニューストピック：\n{ai_response}"
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
    picked_topic = random.choice(topic)
    picked_place = random.choice(place)

    # make openai parameter
    input = []
    text = f'pick one {picked_topic} in {picked_place} countries then talk about it in japanese'
    new_message = {"role":"user", "content":text}
    input.append(new_message)

    # send message to openai api
    ai_response = module_openai.openai_chat_completion(chat=input)
    print(ai_response)

   # traslate from japanese to english for image creation prompt
   translator = Translator()
   translated = translator.translate(ai_response, src='ja', dest='en')
   print(translated)
   translated_en = translated.text

    # generate image by openai
    response = module_openai.openai_create_image(translated_en)

    # save image as file
    image_path = f"/tmp/image_{FACEBOOK_PAGE_ID}.png"
    for data, n in zip(response["data"], range(1)):
        img_data = base64.b64decode(data["b64_json"])
        with open(image_path, "wb") as f:
            f.write(img_data)

    # Initialize a Facebook Graph API object
    graph = facebook.GraphAPI(FACEBOOK_PAGE_ACCESS_TOKEN)

    # Open the image file to be uploaded
    with open(image_path, 'rb') as image:
        # Upload the image to Facebook and get its ID
        photo = graph.put_photo(image, album_id=FACEBOOK_PAGE_ID, caption=ai_response)

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
    print(request.headers)

    data = request.get_json()
    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                # Check if the message is a text message
                if messaging_event.get('message'):
                    sender_id = messaging_event['sender']['id']
                    message_text = messaging_event['message']['text']
                    # making thread for openai handling to avoid retry
                    subthread = threading.Thread(target=handle_message_facebook, args=(message_text, sender_id))
                    subthread.start()
    print("finish request")
    return "ok", 200

# handle facebook message by webhook
def handle_message_facebook(message_text, sender_id):
    print(message_text)
    # send message to openai
    if "reset" in message_text:
        model_openai_chat_log.delete_logs(user_id=sender_id)
        message_text = "reset chat logs!"
    else:
        message_text = module_openai.openai_chat(text=message_text, user_id=sender_id)
    print(message_text)
    send_message(sender_id, message_text)

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
