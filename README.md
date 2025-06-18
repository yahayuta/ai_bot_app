# ai_bot_app

A Python-based application for integrating multiple AI APIs (OpenAI, Gemini Pro, Stable Diffusion) with LINE and Facebook Messenger bots. This project demonstrates how to build, deploy, and operate a multi-platform conversational AI system with image and text generation capabilities.

## Features
- **LINE Bot Integration**: Handles text and audio messages, supports chat, image generation (OpenAI DALL-E, Stability AI), and chat log management.
- **Facebook Messenger Bot Integration**: Auto-posts news summaries, AI-generated images, and supports chat with image descriptions using OpenAI and Gemini APIs.
- **Multi-Model Support**: Utilizes OpenAI (GPT, Whisper, DALL-E), Google Gemini (chat, vision, Imagen), and Stability AI for various AI tasks.
- **Chat Log Storage**: Stores and retrieves chat logs using Google BigQuery for context-aware conversations.
- **Image Storage**: Uploads generated images to Google Cloud Storage for public access.
- **Cloud Native**: Designed for deployment on Google Cloud Run.

## Main Modules
- `main.py`: Flask app entry point, registers LINE and Facebook blueprints.
- `handle_line.py`: Handles LINE webhook, routes messages, manages chat/image generation, and chat logs.
- `handle_facebook.py`: Handles Facebook webhook, auto-posts news/images, manages chat/image generation, and chat logs.
- `module_openai.py`: Functions for OpenAI chat, Whisper (audio transcription), and DALL-E image generation.
- `module_gemini.py`: Functions for Gemini chat, vision, and Imagen image generation.
- `module_stability.py`: Functions for image generation using Stability AI.
- `module_gcp_storage.py`: Uploads files to Google Cloud Storage.
- `model_chat_log.py`: Manages chat logs in Google BigQuery.
- `module_common.py`: Common topics, places, and patterns for prompt generation.

## Deployment
Update your environment variables for API keys and GCP project info. Deploy to Cloud Run:

```sh
gcloud run deploy ai-bot-app --allow-unauthenticated --region=asia-northeast1 --project=yahayuta --source .
```

## Requirements
- Python 3.9+
- Flask
- requests
- line-bot-sdk
- facebook-sdk
- google-cloud-bigquery
- google-cloud-storage
- google-generativeai
- Pillow
- stability-sdk

Install dependencies:
```sh
pip install -r requirements.txt
```

## Environment Variables
- `OPENAI_TOKEN`: OpenAI API key
- `GEMINI_TOKEN`: Google Gemini API key
- `STABILITY_KEY`: Stability AI API key
- `LINE_API_TOKEN`: LINE Messaging API token
- `FACEBOOK_PAGE_ACCESS_TOKEN`: Facebook Page access token
- `FACEBOOK_PAGE_VERIFY_TOKEN`: Facebook Page verify token
- `FACEBOOK_PAGE_ID`: Facebook Page ID
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to GCP service account JSON

## Notes
- Edit `module_common.py` to customize topics, places, and patterns for prompt generation.
- Ensure your GCP project has BigQuery and Cloud Storage enabled.
- Webhook URLs for LINE and Facebook must be set in their respective developer consoles.

---

This project is a template for building advanced, multi-platform AI chatbots with extensible API support and cloud deployment.
