from flask import Flask, request, jsonify
import google.generativeai as genai
GOOGLE_API_KEY='AIzaSyBV6WygToEtDgr1GDCNdHOnCUP18AXeO7A'
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# App initialization

app = Flask(__name__)
prompt='''
You are an excellent Customer Service Assistant with excellent hold in technical services and you are tasked to get the details of the customer who is interacting with you by asking them in a conversational way.

Dont ask all the fields at once be conversational and ask 1 thing at a time.


The details that you need to get are 
Full Name: String Format First_Name Middle_Name Last_Name
Nature of Issue: String Format New_Issue || Exist_Issue
Contact: Number phone_number
Address with pincode: String Format 
Details of Issue: String format (Long Paragraph)
Preffered date and time for technical assistants visit: Date and period of day (Morning || Evening || Night)

You have to be very polite and in a way interactive with the user and not force him to provide information necessarily. If the user doesnt give any information do not force them to give. just leave it blank. 
once you get the details tell the user that the technical person will be reaching at their preferred time at their place
'''



messages=[]
messages.append({
    'role':'user',
    'parts':[prompt]})

messages.append({
    'role':'model',
    'parts':"What's Your name?"           
    })
messages.append({
    'role':'user',
    'parts':"Hi"
  })
messages.append({
    'role':'model',
    'parts':"Hi, there, thank you for contacting us! My name is , and I'm here to assist you today. Could you tell me your full name so I can address you properly?"
  })

@app.route('/getres', methods=['POST'])
def process_string():
    # Get the string from the request
    data = request.get_json()
    message= data['input_string']

    # Process the string (You can replace this with your processing logic)
    # user bolega
    
    print("You:",message)
    messages.append({
            'role':'user',
            'parts':[message]
    })
    response = model.generate_content(messages)
    print(response)
    messages.append({
            'role':'model',
            'parts':[response.text]
        })
    # Respond with the processed string
    # response = {'processed_string': processed_string}
    return response.text # bot ka jayega

if __name__ == '__main__':
    app.run(debug=True)
