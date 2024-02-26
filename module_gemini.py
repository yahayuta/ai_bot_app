"""
At the command line, only need to run once to install the package via pip:

$ pip install google-generativeai
"""

import os
import model_chat_log
import google.generativeai as genai

genai.configure(api_key=os.environ.get('GEMINI_TOKEN', ''))

# Set up the model
generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

# send chat message data
def gemini_chat(text, user_id):
    try:
      # get chat history from database
      history = model_chat_log.get_logs_gemini(user_id=user_id)
      print(history)
      # send prompt and extract result
      convo = model.start_chat(history=history)
      convo.send_message(text)
      print(convo.last.text)
      return convo.last.text
    except Exception as e:
        print(e)
        return f"Gemini returns system Error, try your question again: {e}"
