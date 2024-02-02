import json
import time
from datetime import datetime
import os
import re
from prompts import assistant_instructions


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

        world_model_file = client.files.create(file=open("storage_json/world_storage.json", "rb"),
                                               purpose='assistants')
        character_model_file = client.files.create(file=open("storage_json/character_storage.json", "rb"),
                                                   purpose='assistants')

        assistant = client.beta.assistants.create(
            # Change prompting in prompts.py file
            instructions=assistant_instructions,
            model="gpt-4-1106-preview")

        # Create a new assistant.json file to load on future runs
        with open(assistant_file_path, 'w') as file:
            json.dump({'assistant_id': assistant.id}, file)
            print("Created a new assistant and saved the ID.")

        assistant_id = assistant.id

    return assistant_id


# Clock to send periodic updates
def start_periodic_check(interval, function, *args):
    next_call = time.time()
    while True:
        function(*args)
        next_call = next_call + float(interval)
        time.sleep(next_call - time.time())


def generate_current_time():
    now = datetime.now()
    current_time = now.strftime("%Y/%m/%d %H:%M:%S")
    return current_time


def parse_user_message(message):
    # Extract the values of the relevant variables using regular expressions
    variables = re.findall(r'\!(.*?)\! (.*?)\n', message)
    variables_dict = {var[0]: var[1] for var in variables}
    return variables_dict


def send_message(client, assistant_id, thread_id, message):
    client.beta.threads.messages.create(thread_id=thread_id,
                                        role="user",
                                        content=message)
    run = client.beta.threads.runs.create(thread_id=thread_id,
                                          assistant_id=assistant_id)
    return run.id


def receive_messages(client, thread_id, run_id):
    run = client.beta.threads.runs.retrieve(thread_id=thread_id,
                                            run_id=run_id)
    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
    messages = client.beta.threads.messages.list(
        thread_id=thread_id)
    message = messages.data[0]
    return message.content[0].text.value


def append_event_to_world(world_event):
    world_path = 'storage_json/world_storage.json'
    with open(world_path, 'r') as world_file:
        data = json.load(world_file)
    data['world_events'].append(world_event)
    with open(world_path, 'w') as file:
        json.dump(data, file, indent=4)


def update_character_file(character_file_updates):
    character_path = 'storage_json/character_storage.json'
    with open(character_path, 'r') as character_file:
        data = json.load(character_file)
    for key in character_file_updates:
        if key in data:
            data[key] = character_file_updates[key]
    with open(character_path, 'w') as file:
        json.dump(data, file, indent=4)


def parse_world_message(response):
    print(response)
    # 1. Append to world file
    # TODO Check this regex, runs into problems sometimes
    #world_file_pattern = re.compile(r'\!Time\! "(.+?)"\s+\!Output\! "(.+?)"', re.DOTALL)
    world_file_pattern = re.compile(r'!Time!\s+(.+?)\s+!Output!\s+(.+)', re.DOTALL)
    world_file_match = world_file_pattern.search(response)
    if world_file_match:
        # Extract the matched groups
        world_event = {
            'timestamp': world_file_match.group(1),
            'event_description': world_file_match.group(2)
        }
        append_event_to_world(world_event)
    else:
        print("No match found in the response.")

    # 2. Adjust character file
    user_file_pattern = re.compile(
        r'!Current Time Stamp!\s+(.+?)\s+!Character Memory!\s+([\s\S]+?)\s+!Is Harry texting the user\?!\s+(\w+):\s*?([\s\S]+?)?\s+!Other keys to be updated\?! (\w+)(?:: ([^\n]+))?',
        re.DOTALL)
    user_file_match = user_file_pattern.search(response)

    character_timestamp = user_file_match.group(1)

    character_file_updates = {
        "Character’s Memory": user_file_match.group(2)
    }

    # Handling "Is Harry texting the user?"
    harry_texting = user_file_match.group(3)
    if harry_texting == "YES":
        message_to_user = user_file_match.group(4).strip(": ")
        print(message_to_user)

    # Handling "Other keys to be updated?"
    other_keys_pattern = re.compile(r'([^:]+): ([^:]+)')
    other_keys = user_file_match.group(5)
    if other_keys == "YES":
        other_keys_data = user_file_match.group(6)
        if other_keys_data:  # Checking if other_keys_data is not None
            for key, value in other_keys_pattern.findall(other_keys_data):
                character_file_updates[key.strip()] = value.strip()
    update_character_file(character_file_updates)


def message_from_system_into_assistant(client, assistant_id, thread_id):
    character_path = 'storage_json/character_storage.json'
    world_path = 'storage_json/world_storage.json'

    # Read character file
    with open(character_path, 'r') as character_file:
        character = character_file.read()

    # Read world file
    with open(world_path, 'r') as world_file:
        world = world_file.read()

    # Generate current timestamp
    current_time = generate_current_time()

    # Craft final input message
    message = f"""
    [Character file] {character}
    [World file] {world} 
        [Time] {current_time}
    [World Status Update Request] What is happening right now?
    """

    # Send world query to Assistant API
    run_id = send_message(client, assistant_id, thread_id, message)

    # Receive the file updates and update character and world
    response = receive_messages(client, thread_id, run_id)

    # Parse the results into a dictionary
    parse_world_message(response)
