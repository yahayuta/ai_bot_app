import os
import requests
import openai

from flask import Flask

openai.api_key = os.environ.get('OPENAI_TOKEN', '')
AI_ENGINE = 'gpt-3.5-turbo'

app = Flask(__name__)

@app.route("/openai", methods=["POST"])
def openai():
    text = request.form["text"]
    prompt = []
    new_message = {"role": "user", "content": text}
    prompt.append(new_message)

    print(prompt)

    result = openai.ChatCompletion.create(model=AI_ENGINE, messages=prompt)

    ai_response = result.choices[0].message.content
    print(ai_response)

    return ai_response
    
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
