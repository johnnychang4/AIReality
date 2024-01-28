import os
import threading
import time
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
client = OpenAI(api_key=OPENAI_API_KEY)

# 2. Create the assistant
assistant_id = functions.create_assistant(client)
print("Assistant created with ID:", assistant_id)

# 3. Create the thread for the conversation initialized by the user
thread = client.beta.threads.create()
print("New conversation started with thread ID:", thread.id)

# 4. Start the system thread for world updates to the Assistant API
interval = os.getenv('WORLD_UPDATE_INTERVAL')
system_thread = threading.Thread(target=functions.start_periodic_check,
                                 args=(interval, functions.message_from_system_into_assistant, client, assistant_id,
                                       thread.id))
system_thread.daemon = True
system_thread.start()
# ---------------------------------------------------------------------------------------------------------------------


while True:
    # TODO Hunter - Receive that from ManyChat
    user_input = input("Enter your message (or 'exit' to quit): ")
    if user_input.lower() == 'exit':
        break

    # Generate timestamp-based message from user
    current_time = functions.generate_current_time()
    modified_user_message = "[Time] " + current_time + " [Text from User] " + user_input

    # Send message to Assistant API
    run_id = functions.send_message(client, assistant_id, thread.id, modified_user_message)
    print("Run started with ID:", run_id)

    # Receive message from Assistant API
    start_time = time.time()
    while time.time() - start_time < 8:
        res = functions.receive_messages(client, thread.id, run_id)
        character_answer = functions.parse_user_message(res)
        current_time = time.time()
        response_time = character_answer["Expected response time"]
        # delay = response_time - current_time
        delay = 0
        # If the desired time is in the future, delay the print
        # TODO Hunter - Send that to ManyChat
        if delay > 0:
            time.sleep(delay)
            print(character_answer["Harry response to text message"])
        else:
            print(character_answer["Harry response to text message"])
