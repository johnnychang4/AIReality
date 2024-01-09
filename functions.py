import json
import time
from datetime import datetime

import requests
import os
from openai import OpenAI
from openai.types.beta import assistant

import Client
import prompts
from prompts import assistant_instructions
from dotenv import load_dotenv


# Load environment variables from .env file
# load_dotenv()

# Now you can access your API key
# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Init OpenAI Client
# client = OpenAI(api_key=OPENAI_API_KEY)


# Add lead to Airtable
# def create_lead(name, phone):
#   url = "https://api.airtable.com/v0/appg9Gl6U3S5prIw7/Accelerator%20Leads"
#   headers = {
#       "Authorization": AIRTABLE_API_KEY,
#       "Content-Type": "application/json"
#   }
#   data = {"records": [{"fields": {"Name": name, "Phone": phone}}]}
#   response = requests.post(url, headers=headers, json=data)
#   if response.status_code == 200:
#     print("Lead created successfully.")
#     return response.json()
#   else:
#     print(f"Failed to create lead: {response.text}")


# Create or load assistant
def create_assistant(client):
    assistant_file_path = 'assistant.json'

    # If there is an assistant.json file already, then load that assistant
    if os.path.exists(assistant_file_path):
        with open(assistant_file_path, 'r') as file:
            assistant_data = json.load(file)
            assistant_id = assistant_data['assistant_id']
            print("Loaded existing assistant ID.")
    else:
        # If no assistant.json is present, create a new assistant using the below specifications

        # To change the knowledge document, modify the file name below to match your document If you want to add
        # multiple files, paste this function into ChatGPT and ask for it to add support for multiple files file =
        # client.files.create(file=open("knowledge.docx", "rb"), purpose='assistants')

        world_model_file = client.files.create(file=open("storage_json/world_storage.json", "rb"),
                                               purpose='assistants')
        character_model_file = client.files.create(file=open("storage_json/character_storage.json", "rb"),
                                                   purpose='assistants')

        assistant = client.beta.assistants.create(
            # Change prompting in prompts.py file
            instructions=assistant_instructions,
            model="gpt-4-1106-preview",
            tools=[
                {
                    "type": "retrieval"  # This adds the knowledge base as a tool
                },
                {
                    # "type": "function",  # This adds the lead capture as a tool
                    # "function": {
                    #     "name": "create_lead",
                    #     "description":
                    #     "Capture lead details and save to Airtable.",
                    #     "parameters": {
                    #         "type": "object",
                    #         "properties": {
                    #             "name": {
                    #                 "type": "string",
                    #                 "description": "Full name of the lead."
                    #             },
                    #             "phone": {
                    #                 "type":
                    #                 "string",
                    #                 "description":
                    #                 "Phone number of the lead including country code."
                    #             }
                    #         },
                    #         "required": ["name", "phone"]
                    #     }
                    # }
                }
            ],
            file_ids=[world_model_file.id, character_model_file.id])

        # Create a new assistant.json file to load on future runs
        with open(assistant_file_path, 'w') as file:
            json.dump({'assistant_id': assistant.id}, file)
            print("Created a new assistant and saved the ID.")

        assistant_id = assistant.id

    return assistant_id


# Live clock to trigger function call whenever interval passes
def start_periodic_check(interval, function, *args):
    next_call = time.time()
    while True:
        function(*args)
        next_call = next_call + interval
        time.sleep(next_call - time.time())


# Retrieve world state updates
def get_world_events(assistant_id, thread_id):
    run_id = Client.send_message(assistant_id, thread_id, generate_current_time() + ": " + prompts.get_world_updates)
    response = Client.receive_messages(thread_id, run_id)
    print(response)


def generate_current_time():
    now = datetime.now()
    current_time = now.strftime("%Y/%m/%d %I:%M%p")
    return current_time


# This function is triggered by the system to AI Assistant:
#    -  Generate a specified [timestamp[specified_timestamp]],
#    -  Send "[Timestamp] World Status Update Request: What is happening right now?" to AI Assistant
def message_from_system_into_assistant(assistant_id, thread_id):
    # 1. Query world state for updates
    current_time = generate_current_time()
    message = "[" + current_time + "]" + prompts.get_world_updates
    Client.send_message(assistant_id, thread_id, message)

    # 2. Receive updates and parse them for further processing
    response = Client.receive_messages(assistant_id, thread_id)

    # TODO Parse answer into A. world updates B. Potters internal thought and write


def call_endpoint_at_time(url, desired_time):
    # Calculate the delay in seconds
    delay = (desired_time - datetime.now()).total_seconds()

    # If the time is in the future, wait until that time
    if delay > 0:
        time.sleep(delay)
    # TODO Make the call to the endpoint
