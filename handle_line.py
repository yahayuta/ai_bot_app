import os
import requests
import json
import model_openai_chat_log
import module_openai
import base64
import time

from flask import request
from linebot import LineBotApi
from flask import Blueprint
from google.cloud import storage

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
    else:
        text=event["message"]["text"]
        if "reset" in text:
            # delete all chat log from bigquery
            model_openai_chat_log.delete_logs(user_id=user_id)
            response_text = "reset chat logs!"
        elif "genimg" in text:

            try:
                # generate image by openai
                response = module_openai.openai_create_image(text.replace("genimg", ""))

                # save image as file
                image_path = f"/tmp/image_{user_id}.png"
                for data, n in zip(response["data"], range(1)):
                    img_data = base64.b64decode(data["b64_json"])
                    with open(image_path, "wb") as f:
                        f.write(img_data)

                current_time = int(time.time())
                current_time_string = str(current_time)

                # Uploads a file to the Google Cloud Storage bucket
                image_url = upload_to_bucket(current_time_string, image_path, "ai-bot-app")
                print(image_url)
            except Exception as e:
                error_message = str(e)
                response_text = f"System Error!!!{error_message}"

        elif "text" in type:
            response_text = module_openai.openai_chat(text, user_id=user_id)

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

@line_app.route('/remove_bucket_imgs', methods=['GET'])
def remove_bucket_imgs():
    # Delete all files from a Google Cloud Storage bucket.
    delete_bucket_files("ai-bot-app")
    return "ok", 200

# Delete all files from a Google Cloud Storage bucket.
def delete_bucket_files(bucket_name):
    # Create a Cloud Storage client
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # List all blobs in the bucket
    blobs = bucket.list_blobs()

    # Delete each blob in the bucket
    for blob in blobs:
        blob.delete()
        print(f"Deleted {blob.name}.")

    print(f"All files in {bucket_name} have been deleted.")

#  Uploads a file to the Google Cloud Storage bucket
def upload_to_bucket(blob_name, file_path, bucket_name):
    # Create a Cloud Storage client
    storage_client = storage.Client()

    # Get the bucket that the file will be uploaded to
    bucket = storage_client.bucket(bucket_name)

    # Create a new blob and upload the file's content
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)

    # Make the blob publicly viewable
    blob.make_public()

    # Return the public URL of the uploaded file
    return blob.public_url
