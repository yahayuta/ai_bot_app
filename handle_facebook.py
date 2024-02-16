import os
import requests
import json
import threading
import facebook
import random
import model_openai_chat_log
import module_openai
import io
import time
import module_gcp_storage

from flask import request
from flask import Blueprint
from newsapi import NewsApiClient
from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation

FACEBOOK_PAGE_ACCESS_TOKEN =  os.environ.get('FACEBOOK_PAGE_ACCESS_TOKEN', '')
FACEBOOK_PAGE_VERIFY_TOKEN =  os.environ.get('FACEBOOK_PAGE_VERIFY_TOKEN', '')
FACEBOOK_PAGE_ID = os.environ.get('FACEBOOK_PAGE_ID', '')
NEWS_API_KEY = os.environ.get('NEWS_API_KEY', '')
STABILITY_KEY = os.environ.get('STABILITY_KEY', '')

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

cartoons = [
    "Naruto",
    "Dragon Ball Z",
    "One Piece",
    "Sailor Moon",
    "Pokémon",
    "Attack on Titan",
    "My Hero Academia",
    "Death Note",
    "Fullmetal Alchemist",
    "Bleach",
    "Neon Genesis Evangelion",
    "Cowboy Bebop",
    "Spirited Away",
    "Demon Slayer: Kimetsu no Yaiba",
    "Tokyo Ghoul",
    "One Punch Man",
    "Hunter x Hunter",
    "Fairy Tail",
    "JoJo's Bizarre Adventure",
    "Yu Yu Hakusho",
    "Mob Psycho 100",
    "Akira",
    "Your Name",
    "Sword Art Online",
    "Naruto Shippuden",
    "Death Parade",
    "Ghost in the Shell",
    "Ranma ½",
    "Black Clover",
    "Digimon",
    "Initial D",
    "Gurren Lagann",
    "Inuyasha",
    "Cardcaptor Sakura",
    "Gintama",
    "The Promised Neverland",
    "Parasyte -the maxim-",
    "Code Geass",
    "Trigun",
    "Rurouni Kenshin",
    "Kill la Kill",
    "Wolf's Rain",
    "Fate/stay night",
    "Berserk",
    "Tokyo Mew Mew",
    "Slam Dunk",
    "Detective Conan (Case Closed)",
    "Doraemon",
    "Astro Boy",
    "Kimba the White Lion (Jungle Emperor)",
    "Speed Racer (Mach GoGoGo)",
    "Heidi, Girl of the Alps",
    "Princess Knight (Ribon no Kishi)",
    "Sazae-san",
    "Lupin III",
    "Cyborg 009",
    "Gatchaman (Science Ninja Team Gatchaman)",
    "Dragon Ball",
    "Mazinger Z",
    "Candy Candy",
    "Getter Robo",
    "Space Battleship Yamato (Star Blazers)",
    "Tiger Mask",
    "GeGeGe no Kitaro",
    "Jungle Emperor Leo (Leo the Lion)",
    "Obake no Q-tarō",
    "Akage no Anne (Anne of Green Gables)",
    "Princess Sarah (A Little Princess Sara)",
    "Galaxy Express 999",
    "The Rose of Versailles (Versailles no Bara)",
    "Devilman",
    "Future Boy Conan",
    "Tetsujin 28-go (Gigantor)",
    "Urusei Yatsura (Lum Invader)",
    "The Adventures of Hutch the Honeybee",
    "Dokonjō Gaeru (The Gutsy Frog)",
    "Captain Tsubasa",
    "Maison Ikkoku",
    "Nausicaä of the Valley of the Wind",
    "Kinnikuman (Muscle Man)",
    "Science Ninja Team Gatchaman",
    "Lupin III: Part II",
    "Ganbare!! Tabuchi-kun!!",
    "Sally the Witch (Mahōtsukai Sarī)",
    "Yatterman",
    "Himitsu no Akko-chan (Secret Akko-chan)",
    "The Snow Queen",
    "Panda! Go, Panda!",
    "Space Pirate Captain Harlock",
    "Dokaben",
    "Tensai Bakabon",
    "Combattler V",
    "Casshan",
    "Cutie Honey",
    "Magical Princess Minky Momo",
    "Gekisou! Rubenkaiser",
    "Hana no Ko Lunlun"
]

patterns = [
    "illustration",
    "stencil art",
    "crayon",
    "crayon art",
    "chalk",
    "chalk art",
    "etching",
    "oil paintings",
    "ballpoint pen",
    "ballpoint pen art",
    "colored pencil",
    "watercolor",
    "Chinese watercolor",
    "pastels",
    "woodcut",
    "charcoal",
    "line drawing",
    "screen print",
    "photocollage",
    "storybook illustration",
    "newspaper cartoon",
    "vintage illustration from 1960s",
    "vintage illustration from 1980s",
    "anime style",
    "anime style, official art",
    "manga style",
    "Studio Ghibli style",
    "kawaii",
    "pixel art",
    "screenshot from SNES game",
    "vector illustration",
    "sticker art",
    "3D illustration",
    "cute 3D illustration in the style of Pixar",
    "Octane Render",
    "digital art",
    "2.5D",
    "isometric art",
    "ceramic art",
    "geometric art",
    "surrealism",
    "Dadaism",
    "metaphysical painting",
    "orphism",
    "cubism",
    "suprematism",
    "De Stijl",
    "futurism",
    "expressionism",
    "realism",
    "impressionism",
    "Art Nouveau",
    "baroque painting",
    "rococo painting",
    "mannerism painting",
    "bauhaus painting",
    "ancient Egyptian papyrus",
    "ancient Roman mosaic",
    "ukiyo-e",
    "painted in the style of Vincent van Gogh",
    "painted in the style of Alphonse Mucha",
    "painted in the style of Sophie Anderson",
    "painting by Vincent van Gogh",
    "painting by Alphonse Mucha",
    "painting by Sophie Anderson",  
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
    text = f'pick one {picked_topic} in {picked_place} countries then talk about it very shortly'
    new_message = {"role":"user", "content":text}
    input.append(new_message)

    # send message to openai api
    ai_response = module_openai.openai_chat_completion(chat=input)
    print(ai_response)

    # generate image by openai
    response = module_openai.openai_create_image(ai_response)

    # save image as file
    url = response.data[0].url
    response = requests.get(url)
    image_path = f"/tmp/image_{FACEBOOK_PAGE_ID}.png"
    with open(image_path, 'wb') as file:
        file.write(response.content)
    
    # openai vision api making image details
    ai_response = module_openai.openai_vision(ai_response, url)

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
    cartoon = random.choice(cartoons)
    pattern = random.choice(patterns)

    prompt = f"{cartoon}, {pattern}"

    print(prompt)

    # generate image by stability
    stability_api = client.StabilityInference(key=STABILITY_KEY, verbose=True)
    answers = stability_api.generate(prompt=prompt)

    current_time = int(time.time())
    current_time_string = str(current_time)
    
    # save image as file
    image_path = f"/tmp/image_{current_time_string}.png"
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                print("NSFW")
            if artifact.type == generation.ARTIFACT_IMAGE:
                img = Image.open(io.BytesIO(artifact.binary))
                img.save(image_path)

    # Uploads a file to the Google Cloud Storage bucket
    image_url = module_gcp_storage.upload_to_bucket(current_time_string, image_path, "ai-bot-app")

    print(image_path)
    print(image_url)

    # openai vision api making image details
    ai_response = module_openai.openai_vision(prompt, image_url)

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
    reply_text = ""
    # send message to openai
    if "reset" in message_text:
        model_openai_chat_log.delete_logs(user_id=sender_id)
        reply_text = "reset chat logs!"
    else:
        reply_text = module_openai.openai_chat(text=message_text, user_id=sender_id)
    print(reply_text)
    send_message(sender_id, reply_text)

    # save chat logs with ai
    model_openai_chat_log.save_log(user_id=sender_id, role="user", msg=reply_text)
    model_openai_chat_log.save_log(user_id=sender_id, role="assistant", msg=reply_text)

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
