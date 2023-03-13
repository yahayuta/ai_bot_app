import os
import requests
import openai
import json

from flask import Flask
from flask import request

openai.api_key = os.environ.get('OPENAI_TOKEN', '')
LINE_API_TOKEN =  os.environ.get('LINE_API_TOKEN', '')
AI_ENGINE = 'gpt-3.5-turbo'

app = Flask(__name__)

@app.route("/openai_gpt", methods=["POST"])
def openai_gpt():
    text = request.form["text"]
    input = []
    new_message = {"role": "user", "content": text}
    input.append(new_message)

    print(input)

    result = openai.ChatCompletion.create(model=AI_ENGINE, messages=input)

    ai_response = result.choices[0].message.content
    print(ai_response)

    return ai_response

@app.route("/openai_gpt_line", methods=["POST"])
def openai_gpt_line():

    # extract line message event parameters
    request_json = request.json
    print(request_json)
    events = request_json["events"]
    event = events[0]
    text = event["message"]["text"]
    replyToken = event["replyToken"]

    # building openai api parameters
    input = []
    new_message = {"role": "user", "content": text}
    input.append(new_message)

    print(input)

    # send message to ai
    result = openai.ChatCompletion.create(model=AI_ENGINE, messages=input)
    ai_response = result.choices[0].message.content

    print(replyToken)

    # extract ai response and reply to line
    message = {"type":"text", "text":ai_response}
    messages = [message]
    data = {"replyToken": replyToken, "messages": messages}
    headers = {'content-type': 'application/json', 'Authorization': 'Bearer '+LINE_API_TOKEN }

    res = requests.post("https://api.line.me/v2/bot/message/reply", data=json.dumps(data), headers=headers)
    print(res.json())

    return "ok"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
