import os
import openai

from flask import Flask
from flask import request

openai.api_key = os.environ.get('OPENAI_TOKEN', '')
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
    return "hoge"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
