
import time
import os
from erdos.channel import Channel
from dotenv import load_dotenv


load_dotenv()


def test_chat_session():
    """Test adding multiple conversations to a channel and storing them,
    then retrieving them from the database.
    """

    channel = Channel("channel", os.getenv("OPENAI_API_KEY"))
    conversation = channel.add_conversation()
    conversation.add_message("What is 2+2?")
    conversation.add_message("Add 4 to previous result")
    second_conversation = channel.add_conversation(3)
    second_conversation.add_message("What is 3*3?")
    second_conversation.add_message("Add 1 to the response")

    time.sleep(5)

    print(conversation.get_messages())
    assert '8' in conversation.get_messages().messages[-1].content
    assert '10' in second_conversation.get_messages().messages[-1].content

    conversation.store()
    channel = Channel("channel_2", os.getenv("OPENAI_API_KEY"))
    conversation = channel.add_conversation(1)
    conversation.retrieve()
    conversation.add_message("Add 7 to previous result")

    time.sleep(5)
    assert '15' in conversation.get_messages().messages[-1].content
