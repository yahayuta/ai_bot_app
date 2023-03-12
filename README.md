# ai_bot_app

deploy to gcp cloud run  

```sh
gcloud run deploy ai-bot-app --allow-unauthenticated --region=asia-northeast1 --project=yahayuta --source .
```

test from local environment 

```sh
curl -X POST -d 'text=令和元年の西暦を教えてください' https://xxxx/openai
``