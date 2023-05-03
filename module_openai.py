import os
import openai
import model_openai_chat_log

openai.api_key = os.environ.get('OPENAI_TOKEN', '')

AI_ENGINE = 'gpt-3.5-turbo'

# send audio data
def openai_whisper(file_path):
    print(file_path)
    ai_response = ''
    try:
        # load audio file to openai
        file = open(file_path, "rb")
        transcription = openai.Audio.transcribe("whisper-1", file)
        # print(transcription)
        ai_response = transcription["text"]
    except openai.Error as e:
        ai_response = f"OpenAI returns system Error, try your question again: {e}"
    return ai_response

# send chat message data
def openai_chat(text, user_id):
    # building openai api parameters
    input = model_openai_chat_log.get_logs(user_id=user_id)
    new_message = {"role":"user", "content":text}
    input.append(new_message)

    print(input)

    # send message to openai api
    ai_response = openai_chat_completion(chat=input)

    # save chat logs with ai
    model_openai_chat_log.save_log(user_id=user_id, role="user", msg=text)
    model_openai_chat_log.save_log(user_id=user_id, role="assistant", msg=ai_response)

    return ai_response

# generate image by openai
def openai_create_image(prompt):
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512",
            response_format="b64_json",
        )
    except openai.Error as e:
        print(f"Error: {e}")
    return response

# send message to openai api
def openai_chat_completion(chat):
    ai_response = ''
    try:
        result = openai.ChatCompletion.create(model=AI_ENGINE, messages=chat)
        ai_response = result.choices[0].message.content
    except openai.Error as e:
        ai_response = f"ChatGPT returns system Error, try your question again: {e}"
    return ai_response   