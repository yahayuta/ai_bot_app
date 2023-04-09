import os
import requests
import openai
import json

from flask import Flask
from flask import request
from linebot import LineBotApi
from google.cloud import bigquery

openai.api_key = os.environ.get('OPENAI_TOKEN', '')
LINE_API_TOKEN =  os.environ.get('LINE_API_TOKEN', '')
FACEBOOK_PAGE_ACCESS_TOKEN =  os.environ.get('FACEBOOK_PAGE_ACCESS_TOKEN', '')
FACEBOOK_PAGE_VERIFY_TOKEN =  os.environ.get('FACEBOOK_PAGE_VERIFY_TOKEN', '')
AI_ENGINE = 'gpt-3.5-turbo'

app = Flask(__name__)

@app.route("/")
def hello_world():
    name = os.environ.get("NAME", "World")
    return "Hello {}!".format(name)

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
    data = request.get_json()
    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                # Check if the message is a text message
                if messaging_event.get('message'):
                    sender_id = messaging_event['sender']['id']
                    message_text = messaging_event['message']['text']

                    # send message to openai
                    if "reset" in message_text:
                        delete_logs(user_id=sender_id)
                        message_text = "reset chat logs!"
                    else:
                        message_text = openai_chat(text=message_text, user_id=sender_id)
        
                    send_message(sender_id, message_text)
    return "ok", 200

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
            delete_logs(user_id=user_id)
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
    input = get_logs(user_id=user_id)
    new_message = {"role":"user", "content":text}
    input.append(new_message)

    print(input)

    # send message to openai api
    result = openai.ChatCompletion.create(model=AI_ENGINE, messages=input)
    # print(result)
    
    ai_response = result.choices[0].message.content
    # print(ai_response)

    # save chat logs with ai
    save_log(user_id=user_id, role="user", msg=text)
    save_log(user_id=user_id, role="assistant", msg=ai_response)
    
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

# save chat log into bigquery
def save_log(user_id, role, msg):
    client = bigquery.Client()
    client.query(f'INSERT INTO app.openai_chat_log(user_id,chat,role,created) values(\'{user_id}\',\'\'\'{msg}\'\'\',\'{role}\',CURRENT_DATETIME(\'Asia/Tokyo\'))')

# load chat log from bigquery
def get_logs(user_id):
    client = bigquery.Client()
    query_job = client.query(f'SELECT * FROM app.openai_chat_log where user_id = \'{user_id}\' order by created;')
    rows = query_job.result()
    print(rows.total_rows)
    logs = []
    for row in rows:
        log = {"role": row["role"], "content": row["chat"]}
        logs.append(log)
    return logs

# delete all chat log from bigquery
def delete_logs(user_id):
    client = bigquery.Client()
    client.query(f'DELETE FROM app.openai_chat_log where user_id = \'{user_id}\';')

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
