from flask import Flask, request, jsonify
import google.generativeai as genai
GOOGLE_API_KEY='AIzaSyBV6WygToEtDgr1GDCNdHOnCUP18AXeO7A'
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')
port=8000
# App initialization

app = Flask(__name__)
prompt='''Your name is KrushiMitra, you have been tasked to give the Calendar of crop growth of a particular crop in month and what all are the procedures to be followed to grow a crop in an area. Act like a conversational AI and get all the required details that you want to predict the time of year, ask the user for his details like location(state) and the type of crop he wants to grow. Don't assume my default location rather ask me for it. Give a monthly / quarterly analysis of what needs to be done. show stages of growing the certain crop. dont just give the season but also the steps of farming. you have to give short and to the point answers and only give the task assigned to you by me. If the user speaks in hindi you should respond in hindi. Dont give calendar until the user doesnt provide the name of crop.if a crop cannot be cultivated in the area, suggest the user to grow some other plant that can be profittable.'''



messages=[]
messages.append({
    'role':'user',
    'parts':[prompt]})

messages.append({
    'role':'model',
    'parts':"What's Your state?"           
    })
messages.append({
    'role':'user',
    'parts':"Hi"
  })
messages.append({
    'role':'model',
    'parts':"Hi, there, thank you for contacting us! My name is KrushiMitra, and I'm here to assist you today. Could u pls tell me which state youre from?"
  })

@app.route('/getres', methods=['POST'])
def process_string():
    # Get the string from the request
    data = request.get_json()
    input_string = data['input_string']

    # Process the string (You can replace this with your processing logic)
    # user bolega
    message= input_string
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
@app.route('/',methods=['POST'])
def Hello():
    print("Hello World")
if __name__ == '__main__':
    app.run(port,debug=True)
