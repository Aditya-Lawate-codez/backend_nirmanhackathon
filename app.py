import json
import re
from flask import Flask, request, jsonify
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
app = Flask(__name__)

GOOGLE_API_KEY='AIzaSyBV6WygToEtDgr1GDCNdHOnCUP18AXeO7A'
genai.configure(api_key=GOOGLE_API_KEY)
from pymongo import MongoClient
uri = "mongodb+srv://adityalawate2004:ljYTFSVUS1ZcZQdh@threads.riq9cuf.mongodb.net/?retryWrites=true&w=majority&appName=Threads"    

# App initialization
generation_config = {
    
  "temperature": 0.3,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}
model = genai.GenerativeModel('gemini-1.5-pro', generation_config=generation_config, safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT:HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT:HarmBlockThreshold.BLOCK_NONE,
          
        
    })
prompt='''You are a polite Customer Service Assistant specializing in technical services. Engage the customer in a conversational manner to gather the following details one at a time:

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
"'''



messages=[]
messages.append({
    'role':'user',
    'parts':[prompt]})

messages.append({
    'role':'model',
    'parts':"Hi, there, thank you for contacting us! My name is CVA, and I'm here to assist you today. Could you tell me your full name so I can address you properly?"           
    })

@app.route('/getres', methods=['POST'])
def process_string(msg):
    # Get the string from the request
    data = request.get_json()
    message = data['input_string']
    # message= msg
    messages.append({
            'role':'user',
            'parts':[message]
    })
    response = model.generate_content(messages)
    try:
        part =  response.text or response.candidates[0].content.parts[0] 
    except Exception:
        part = "Error: Could not generate response"
        
    if "```json" in part:
        subpart=f"""{part}"""
        json_data = re.search(r'```json\s*(\{.*?\})\s*```', subpart, re.DOTALL).group(1)
        data = json.loads(json_data)
        client = MongoClient(uri)
        database = client["userInformation"]
        collection = database["users"]
        collection.insert_one(data, )
        client.close()

    # part= response.text
    messages.append({
            'role':'model',
            'parts': part,#[response.text or response.candidates[0].content.parts[0].function_response.response]
        })
    # Respond with the processed string
    # response = {'processed_string': processed_string}
    print(response.text)
    try:
        return response.text
    except Exception:
        return response
if __name__ == '__main__':
    app.run(debug=True)