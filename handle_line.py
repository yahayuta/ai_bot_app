import os
import requests # type: ignore
import json
import model_chat_log
import module_openai
import time
import module_gcp_storage
import module_stability

from flask import request # type: ignore
from linebot import LineBotApi # type: ignore
from flask import Blueprint # type: ignore

LINE_API_TOKEN =  os.environ.get('LINE_API_TOKEN', '')

AI_ENGINE = 'gpt-3.5-turbo'

line_app = Blueprint('handle_line', __name__)

@line_app.route("/openai_gpt_line", methods=["POST"])
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
    message_id = event["message"]["id"]
    # print(type)

    # check chat mode or audio trans chat mode or delete all chat logs mode
    response_text = ""
    image_url = ""

    current_time = int(time.time())
    current_time_string = str(current_time)
    
    if "audio" in type:
        # use line sdk library to get audio file
        line_bot_api = LineBotApi(LINE_API_TOKEN)
        message_content = line_bot_api.get_message_content(message_id)
        file_path = f"/tmp/{user_id}.m4a"
        with open(file_path, 'wb') as fd:
            for chunk in message_content.iter_content():
                fd.write(chunk)

        # trans voice data to text
        trans_text = module_openai.openai_whisper(file_path)
        ai_text = module_openai.openai_chat(text=trans_text, user_id=user_id)
        response_text = f"Q:{trans_text}\nA:{ai_text}"

        # save chat logs
        model_chat_log.save_log(user_id=user_id, role="user", message=trans_text)
        model_chat_log.save_log(user_id=user_id, role="assistant", message=ai_text)
    else:
        text=event["message"]["text"]
        if "reset" in text:
            # delete all chat log from bigquery
            model_chat_log.delete_logs(user_id=user_id)
            response_text = "reset chat logs!"
        elif "genimgsd" in text:
            # generate image by stability
            image_path = f"/tmp/image_{user_id}.png"
            module_stability.generate(text.replace("genimgsd", ""), image_path)

            # Uploads a file to the Google Cloud Storage bucket
            image_url = module_gcp_storage.upload_to_bucket(current_time_string, image_path, "ai-bot-app")
            print(image_url)
        elif "genimg" in text:
            try:
                # generate image by openai   
                image_path = f"/tmp/image_{user_id}.png"
                module_openai.openai_create_image(text.replace("genimg", ""), image_path)
                
                # Uploads a file to the Google Cloud Storage bucket
                image_url = module_gcp_storage.upload_to_bucket(current_time_string, image_path, "ai-bot-app")
                print(image_url)
            except Exception as e:
                error_message = str(e)
                response_text = f"System Error!!!{error_message}"
        elif "text" in type:
            response_text = module_openai.openai_chat(text, user_id=user_id)
            
            # save chat logs
            model_chat_log.save_log(user_id=user_id, role="user", message=text)
            model_chat_log.save_log(user_id=user_id, role="assistant", message=response_text)

    print(replyToken)
    print(response_text)

    # extract ai response and reply to line
    message = {}
    if response_text != "":
        message = {"type":"text", "text":response_text}
    elif image_url != "":
        message = {"type":"image", "originalContentUrl":image_url, "previewImageUrl":image_url}

    messages = [message]
    data = {"replyToken":replyToken, "messages":messages}
    headers = {'content-type':'application/json', 'Authorization':f'Bearer {LINE_API_TOKEN}'}
    res = requests.post("https://api.line.me/v2/bot/message/reply", data=json.dumps(data), headers=headers)
    print(res.json())

    return "ok"
