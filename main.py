import os
import requests
import openai
import json
import threading
import facebook
import random
import model_openai_chat_log
import base64

from flask import Flask
from flask import request
from linebot import LineBotApi

openai.api_key = os.environ.get('OPENAI_TOKEN', '')
LINE_API_TOKEN =  os.environ.get('LINE_API_TOKEN', '')
FACEBOOK_PAGE_ACCESS_TOKEN =  os.environ.get('FACEBOOK_PAGE_ACCESS_TOKEN', '')
FACEBOOK_PAGE_VERIFY_TOKEN =  os.environ.get('FACEBOOK_PAGE_VERIFY_TOKEN', '')
FACEBOOK_PAGE_ID = os.environ.get('FACEBOOK_PAGE_ID', '')

AI_ENGINE = 'gpt-3.5-turbo'

app = Flask(__name__)

topic = [
   "musician or group or band",
   "movie",
   "drama",
   "place"
]

@app.route("/openai_gpt_facebook_autopost_image")
def openai_gpt_facebook_autopost_image():

    # pick topic randomly
    picked_topic = random.choice(topic)

    # make openai parameter
    input = []
    text = f'pick one famous japanese {picked_topic} then talk about it in japanese'
    new_message = {"role":"user", "content":text}
    input.append(new_message)

    # send message to openai api
    result = openai.ChatCompletion.create(model=AI_ENGINE, messages=input)    
    ai_response = result.choices[0].message.content
    print(ai_response)

    response = openai.Image.create(
        prompt=ai_response,
        n=1,
        size="512x512",
        response_format="b64_json",
    )

    image_path = f"image_{FACEBOOK_PAGE_ID}.png"
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

@app.route("/openai_gpt_facebook_autopost")
def openai_gpt_facebook_autopost():

    # pick topic randomly
    picked_topic = random.choice(topic)

    # make openai parameter
    input = []
    text = f'pick one famous {picked_topic} all over the world then talk about it in japanese'
    new_message = {"role":"user", "content":text}
    input.append(new_message)

    # send message to openai api
    result = openai.ChatCompletion.create(model=AI_ENGINE, messages=input)    
    ai_response = result.choices[0].message.content
    print(ai_response)

    # Initialize a Facebook Graph API object
    graph = facebook.GraphAPI(FACEBOOK_PAGE_ACCESS_TOKEN)

    # Make a post to the Facebook page
    graph.put_object(
        parent_object=FACEBOOK_PAGE_ID,
        connection_name='feed',
        message=ai_response
    )
    return "ok", 200

@app.route('/openai_gpt_facebook', methods=['GET'])
def openai_gpt_facebook_verify():
    # Facebook requires a challenge token to verify the webhook
    challenge = request.args.get('hub.challenge')
    if FACEBOOK_PAGE_VERIFY_TOKEN == request.args.get('hub.verify_token'):
        return challenge
    else:
        return "Invalid verification token"

@app.route('/openai_gpt_facebook', methods=['POST'])
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
        message_text = openai_chat(text=message_text, user_id=sender_id)
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

@app.route("/openai_gpt_line", methods=["POST"])
def openai_gpt_line():
    # register webhook endpoint this route url to line developer console

    # extract line message event parameters
    request_json = request.json
    print(request_json)
    events = request_json["events"]
    event = events[0]
    replyToken = event["replyToken"]
    type = event["message"]["type"]
    user_id=event["source"]["userId"]
    # print(type)

    # check chat mode or audio trans chat mode or delete all chat logs mode
    response_text = ""
    if "audio" in type:
        trans_text = openai_whisper(message_id=event["message"]["id"], user_id=user_id)
        ai_text = openai_chat(text=trans_text, user_id=user_id)
        response_text = f"Q:{trans_text}\nA:{ai_text}"
    else:
        text=event["message"]["text"]
        if "reset" in text:
            model_openai_chat_log.delete_logs(user_id=user_id)
            response_text = "reset chat logs!"
        elif "text" in type:
            response_text = openai_chat(text, user_id=user_id)

    print(replyToken)
    print(response_text)

    # reply to line ai response
    send_msg_to_line(replyToken=replyToken, text=response_text)

    return "ok"

# send chat message data
def openai_chat(text, user_id):
    # building openai api parameters
    input = model_openai_chat_log.get_logs(user_id=user_id)
    new_message = {"role":"user", "content":text}
    input.append(new_message)

    print(input)

    # send message to openai api
    result = openai.ChatCompletion.create(model=AI_ENGINE, messages=input)
    # print(result)
    
    ai_response = result.choices[0].message.content
    # print(ai_response)

    # save chat logs with ai
    model_openai_chat_log.save_log(user_id=user_id, role="user", msg=text)
    model_openai_chat_log.save_log(user_id=user_id, role="assistant", msg=ai_response)
    
    return ai_response

# send audio data
def openai_whisper(message_id, user_id):
    print(message_id)
    print(user_id)

    # use line sdk library to get audio file
    line_bot_api = LineBotApi(LINE_API_TOKEN)
    message_content = line_bot_api.get_message_content(message_id)
    file_path = f"/tmp/{user_id}.m4a"
    with open(file_path, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

    print(file_path)

    # load audio file to openai
    file = open(file_path, "rb")
    transcription = openai.Audio.transcribe("whisper-1", file)
    # print(transcription)
    return transcription["text"]

# send messages to line through line api
def send_msg_to_line(replyToken, text):
    # extract ai response and reply to line
    message = {"type":"text", "text":text}
    messages = [message]
    data = {"replyToken":replyToken, "messages":messages}
    headers = {'content-type':'application/json', 'Authorization':f'Bearer {LINE_API_TOKEN}'}
    res = requests.post("https://api.line.me/v2/bot/message/reply", data=json.dumps(data), headers=headers)
    print(res.json())

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
