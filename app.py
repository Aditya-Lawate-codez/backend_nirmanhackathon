from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from pymongo import MongoClient
import os
from os.path import join, dirname
from dotenv import load_dotenv
import json
import re
from google.cloud import texttospeech, speech
from google.protobuf.json_format import MessageToJson

app = Flask(__name__)
CORS(app)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
uri = os.environ.get("URI")

generation_config = {
    "temperature": 0.3,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
model = genai.GenerativeModel(
    'gemini-1.5-flash',
    generation_config=generation_config,
    safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    }
)

prompt = '''You are a polite Customer Service Assistant specializing in technical services. Engage the customer in a conversational manner to gather the following details one at a time:

- Contact Number (ask first)
- Full Name (First_Name Middle_Name Last_Name)
- Nature of Issue (New Issue || Existing Issue)
- Address with pincode
- Details of Issue (Long Paragraph)
- Preferred date and time for a technician visit (Date and Morning || Evening || Night)

Do not push for details if the customer is unwilling to provide them. Once all details are collected, confirm the appointment and present the information in the JSON format when the customer says goodbye.
Ask straight forward questions in minimum words
Example JSON:
```json
{
    "name": "first_name middle_name last_name",
    "phoneno": "1234567890",
    "address": "123 Main Street, Florida 401202",
    "problem_detail": "Keyboard not working properly.",
    "nature_of_issue": "Existing",
    "date": "Sunday evening at 8 pm"
}
```
'''

messages = []
messages.append({
'role': 'user',
'parts': [prompt]
})

messages.append({
'role': 'model',
'parts': "Hi, there, thank you for contacting us! My name is CVA, and I'm here to assist you today. Could you tell me your full name so I can address you properly?"
})

@app.route('/getres', methods=['POST'])
def process_string():
    data = request.get_json()
    message = data['input_string']
    messages.append({
        'role': 'user',
        'parts': [message]
    })
    response = model.generate_content(messages)
    try:
        part = response.text or response.candidates[0].content.parts[0]
    except Exception:
        part = "Error: Could not generate response"

    if "```json" in part:
        subpart = f"""{part}"""
        json_data = re.search(r'```json\s*(\{.*?\})\s*```', subpart, re.DOTALL).group(1)
        data = json.loads(json_data)
        client = MongoClient(uri)
        database = client["userInformation"]
        collection = database["users"]
        collection.insert_one(data)
        client.close()

    messages.append({
        'role': 'model',
        'parts': part,
    })
    print(response.text)
    try:
        return jsonify({'response': response.text})
    except Exception:
        return jsonify({'response': "An error occurred."})

@app.route('/synthesize', methods=['POST'])
def synthesize_text():
    client = texttospeech.TextToSpeechClient()
    data = request.get_json()
    text = data['text']
    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL )
    audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3)
    response = client.synthesize_speech(
    input=input_text, voice=voice, audio_config=audio_config )
    audio_content = response.audio_content
    return jsonify({'audioContent': audio_content.decode('ISO-8859-1')})

@app.route('/recognize', methods=['POST'])
def recognize_speech():
    client = speech.SpeechClient()
    audio_data = request.files['audio']
    audio = speech.RecognitionAudio(content=audio_data.read())
    config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=16000,
    language_code="en-US"
    )
    response = client.recognize(config=config, audio=audio)
    result_text = response.results[0].alternatives[0].transcript
    return jsonify({'transcript': result_text})

if __name__ == '__main__':
    app.run(debug=True)