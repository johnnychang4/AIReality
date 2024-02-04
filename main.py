import os
import threading
import time
import openai
from openai import OpenAI
import functions
from packaging import version
from dotenv import load_dotenv
from flask import Flask, request, Response

app = Flask(__name__)

# Storing of thread for each user (multi-user system)
users = {}

# Load environment variables and system
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

# Create client and assistant for this program
client = OpenAI(api_key=OPENAI_API_KEY)
assistant_id = functions.create_assistant(client)
print("Assistant created with ID:", assistant_id)


# Create threads for new users

def create_thread(user, harry):
    # Create OpenAI Thread
    thread = client.beta.threads.create()
    print("New conversation started with thread ID:", thread.id)

    # Create System Thread
    interval = os.getenv('WORLD_UPDATE_INTERVAL')
    system_thread = threading.Thread(target=functions.start_periodic_check,
                                     args=(interval, functions.message_from_system_into_assistant, client, assistant_id,
                                           thread.id, user, harry))
    system_thread.daemon = True
    system_thread.start()
    return thread.id


# ---------------------------------------------------------------------------------------------------------------------


def send_message_to_harry(user_input, thread_id, harry):
    # Generate timestamp-based message from user
    current_time = functions.generate_current_time()
    modified_user_message = "[Time] " + current_time + " [Text from User] " + user_input

    # TODO we could add a queue here later with scheduler
    # Avoids error where both requests interfere (Harry does not answer when error)
    active_run = functions.check_for_active_run(thread_id)
    if not active_run:

        # Send message to OpenAI
        run_id = functions.send_message(client, assistant_id, thread_id, modified_user_message)
        print("Run started with ID:", run_id)

        # Receive message from OpenAI
        res = functions.receive_messages(client, thread_id, run_id)
        character_answer = functions.parse_user_message(res)

        # TODO we can Delay here: delay = response_time - current_time
        # Calculate time for response of Harry
        delay = 0
        current_time = time.time()
        response_time = character_answer["Expected response time"]

        # Extract response of Harry and return
        harry_response = character_answer["Harry response to text message"]
        if delay > 0:
            time.sleep(delay)
            return harry_response

        else:
            return harry_response
    else:
        print("Harry does not reply")
        return None


# Webhook registered with Twilio and hosted on the web (e.g. ngrok)
@app.route('/receive-messages', methods=['POST'])
def handle_post():

    # Extract message of Harry as well as phone numbers
    incoming_msg = request.form.get('Body', '')
    print(f"Incoming message: {incoming_msg}")
    user = request.form.get('From', '')
    harry = request.form.get('To', '')

    # Check if active thread with user exists already, if not create
    if user not in users:
        thread_id = create_thread(user, harry)
        users[user] = (thread_id, harry)

    # Sends message to OpenAI and parses response to output here
    response = send_message_to_harry(incoming_msg, *users[user])

    # If Harry does not answer, empty response is returned
    if response:
        resp = (f"\n"
                f"    <Response>\n"
                f"    <Message>{response} - Received message: {incoming_msg}</Message>\n"
                f"</Response>\n")

        return Response(resp, mimetype='text/xml')
    else:
        return Response('', status=200)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
