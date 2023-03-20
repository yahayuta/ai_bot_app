import os
import requests
import openai
import json

from flask import Flask
from flask import request
from linebot import LineBotApi

openai.api_key = os.environ.get('OPENAI_TOKEN', '')
LINE_API_TOKEN =  os.environ.get('LINE_API_TOKEN', '')
AI_ENGINE = 'gpt-3.5-turbo'

app = Flask(__name__)

@app.route("/")
def hello_world():
    name = os.environ.get("NAME", "World")
    return "Hello {}!".format(name)

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

    print(type)

    # check chat mode or audio trans mode
    ai_response = ""
    if "text" in type:
        ai_response = openai_chat(event["message"]["text"])
    if "audio" in type:
        ai_response = openai_whisper(event["message"]["id"], event["source"]["userId"])

    print(replyToken)

    # extract ai response and reply to line
    message = {"type":"text", "text":ai_response}
    messages = [message]
    data = {"replyToken":replyToken, "messages":messages}
    headers = {'content-type':'application/json', 'Authorization':f'Bearer {LINE_API_TOKEN}'}
    res = requests.post("https://api.line.me/v2/bot/message/reply", data=json.dumps(data), headers=headers)
    print(res.json())

    return "ok"

# send chat message data
def openai_chat(text):
    # building openai api parameters
    input = []
    new_message = {"role":"user", "content":text}
    input.append(new_message)

    print(input)

    # send message to openai api
    result = openai.ChatCompletion.create(model=AI_ENGINE, messages=input)
    print(result)
    return result.choices[0].message.content

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

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
