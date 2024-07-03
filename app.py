from flask import Flask, request, jsonify
import google.generativeai as genai
GOOGLE_API_KEY='AIzaSyBV6WygToEtDgr1GDCNdHOnCUP18AXeO7A'
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

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
In the format of :
{
    "name":"aditya",
    "phoneno":"86868",
    "address":"Vasai 401202",
    "problem_detail":"Keyboard not working",
    "nature_of_issue":"Existing",
    "date":"Sunday evening at 8 pm"
    }
You have to be very polite and in a way interactive with the user and not force him to provide information necessarily. If the user doesnt give any information do not force them to give. just leave it blank. 
once you get the deatils tell the user that the technical assistant will be reaching at their preferred time at their place
after getting all the information you need to give a json representation of the information whenever the user says goodbye.
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
    message = data['input_string']

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
