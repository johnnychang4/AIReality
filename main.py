import json
import os
import time
from flask import Flask, request, jsonify
import openai
from openai import OpenAI
import functions
from packaging import version
from dotenv import load_dotenv


# INITIALIZATION: -----------------------------------------------------------------------------------------------------
# 1. Load environment variables and system
load_dotenv()
required_version = version.parse("1.1.1")
current_version = version.parse(openai.__version__)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if current_version < required_version:
  raise ValueError(
      f"Error: OpenAI version {openai.__version__} is less than the required version 1.1.1"
  )
else:
  print("OpenAI version is compatible.")
# app = Flask(__name__)
client = OpenAI(api_key=OPENAI_API_KEY)

# 2. Create the assitant
assistant_id = functions.create_assistant(client)
print("Assistant created with ID:", assistant_id)



# 3. Create the thread for the conversation initialzied by the user
# @app.route('/start', methods=['GET'])
#def start_conversation():
thread = client.beta.threads.create()
print("New conversation started with thread ID:", thread.id)
  # return jsonify({"thread_id": thread.id})
# ---------------------------------------------------------------------------------------------------------------------


while True:
    user_input = input("Enter your message (or 'exit' to quit): ")
    if user_input.lower() == 'exit':
        break
     # Send message to AI Assistant
    client.beta.threads.messages.create(thread_id=thread.id,
                                        role="user",
                                        content=user_input)

    run = client.beta.threads.runs.create(thread_id=thread.id,
                                          assistant_id=assistant_id)
    print("Run started with ID:", run.id)


    start_time = time.time()
    while time.time() - start_time < 8:
      run_status = client.beta.threads.runs.retrieve(thread_id=thread.id,
                                                   run_id=run.id)
      print("Checking run status:", run_status.status)
  
      if run_status.status == 'completed':
        print("completed action")
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        message_content = messages.data[0].content[0].text
        break

    print(message_content)
    time.sleep(1)
        # Remove annotations
        
    
        
      


    

    # run_status = client.beta.threads.runs.retrieve(thread_id=thread.id,
                                                   #run_id=run.id)

   
   


# COMMUNICATION : ------------------------------------------------------------------------
# 1. This function is triggered when the user sends a whatsapp message: 
#    - Receive [message] from user
#    - Generate a current [timestamp] 
#    - Send [timestamp + message] to the AI Assistant
# @app.route('/chat', methods=['POST'])
# def message_from_user_into_assitant(): 
# - Receive [message] from user: 
  # data = request.json
  # thread_id = data.get('thread_id')
  # user_input = data.get('message', '')
  # if not thread_id:
  #   print("Error: Missing thread_id in /chat")
  #   return jsonify({"error": "Missing thread_id"}), 400
  # print("Received message for thread ID:", thread_id, "Message:", user_input)

# - Generate a current [timestamp]: 







# - Send [timestamp + message] to the AI Assistant:
  # client.beta.threads.messages.create(thread_id=thread_id,
  #                                     role="user",
  #                                     content= user_input)


  # client.beta.threads.messages.create(thread_id=thread_id,
  #                                     role="user",
  #                                     content= [timestamp + user_input])


  # run = client.beta.threads.runs.create(thread_id=thread_id,
                                        # assistant_id=assistant_id)
  # print("Run started with ID:", run.id)

  # send run ID back to ManyChat:
  # return jsonify({"run_id": run.id})

# 2. This function is triggered by the system to AI Assistant: 
#    -  Generate a specified [timestamp[specified_timestamp]],
#    -  Send "[Timestamp] World Status Update Request: What is happening right now?" to AI Assistant
# def message_from_system_into_assitant():
  # - Generate a current [timestamp]: 


  #message = "World Status Update Request: What is happening right now?"


  # Send "[Timestamp] World Status Update Request: What is happening right now?" to AI Assistant:
  # client.beta.threads.messages.create(thread_id=thread_id,
  #                                     role="user",
  #                                     content=user_input)


# 3. Check for status to see if there are functions_callings need to be run
# @app.route('/check', methods=['POST'])
# def check_run_status():
#   data = request.json
#   thread_id = data.get('thread_id')
#   run_id = data.get('run_id')
#   if not thread_id or not run_id:
#     print("Error: Missing thread_id or run_id in /check")
#     return jsonify({"response": "error"})

#   # Start timer ensuring no more than 9 seconds, ManyChat timeout is 10s
#   start_time = time.time()
#   while time.time() - start_time < 8:
#     run_status = client.beta.threads.runs.retrieve(thread_id=thread_id,
#                                                    run_id=run_id)
#     print("Checking run status:", run_status.status)

#     if run_status.status == 'completed':
#       # Get the message from AI and send it to the ManyChat
#       messages = client.beta.threads.messages.list(thread_id=thread_id)
#       message_content = messages.data[0].content[0].text
#       # Remove annotations
#       annotations = message_content.annotations
#       for annotation in annotations:
#         message_content.value = message_content.value.replace(
#             annotation.text, '')
#       print("Run completed, returning response")
#       print(message_content.value) 
#       return jsonify({
#           "response": message_content.value,
#           "status": "completed"
#       })

    # if run_status.status == 'requires_action':
    #   print("Action in progress...")
    #   # Handle the function call
    #   for tool_call in run_status.required_action.submit_tool_outputs.tool_calls:
    #     if tool_call.function.name == "create_lead":
    #       # Process lead creation
    #       arguments = json.loads(tool_call.function.arguments)
    #       output = functions.create_lead(arguments["name"], arguments["phone"])
    #       client.beta.threads.runs.submit_tool_outputs(thread_id=thread_id,
    #                                                    run_id=run_id,
    #                                                    tool_outputs=[{
    #                                                        "tool_call_id":
    #                                                        tool_call.id,
    #                                                        "output":
    #                                                        json.dumps(output)
    #                                                    }])
    # time.sleep(1)

  # print("Run timed out")
  # return jsonify({"response": "timeout"})
# ---------------------------------------------------------------------------------------------------------------------




# PORTAL CONTROL: -----------------------------------------------------------------------------------------------------
# if __name__ == '__main__':
#   app.run(host='0.0.0.0', port=8080)
