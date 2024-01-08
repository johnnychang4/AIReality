from main import client


# TODO We may switch to this class later to make things cleaner
class Client:
    def __init__(self):
        # TODO initialize the assistant here in the future
        pass

    # method to abstract the "write logic" to assistant API


def send_message(assistant_id, thread_id, message):
    client.beta.threads.messages.create(thread_id=thread_id,
                                        role="user",
                                        content=message)
    run = client.beta.threads.runs.create(thread_id=thread_id,
                                          assistant_id=assistant_id)
    return run.id


# method to abstract the "read logic" from assistant API
def receive_messages(thread_id, run_id):
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
