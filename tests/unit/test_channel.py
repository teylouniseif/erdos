import asyncio
import pytest
from unittest.mock import patch
from erdos.channel import Channel


@pytest.fixture
def channel():
    channel = Channel(1, '5')
    yield channel


@patch('erdos.channel.Conversation')
def test_add_conversation(MockConversation, channel):
    """Test add_conversation method of Channel class

    Args:
        channel (Channel): Channel object
    """

    channel.add_conversation(3)
    MockConversation.assert_called_with(3, channel.event_loop, '5')
    # Ensure conversation_id is set from the argument
    assert channel.conversations[3] == MockConversation(
        3, channel.event_loop, '5')

    channel.add_conversation()
    MockConversation.assert_called_with(4, channel.event_loop, '5')
    # Ensure conversation_id is set to the next available id
    assert channel.conversations[4] == MockConversation(
        4, channel.event_loop, '5')

    channel.add_conversation(6)
    MockConversation.assert_called_with(6, channel.event_loop, '5')
    # Ensure conversation_id is set from the argument
    assert channel.conversations[6] == MockConversation(
        6, channel.event_loop, '5')

    # Ensure ValueError is raised when conversation_id already exists
    with pytest.raises(ValueError, match=f"Conversation with id {6} already exists"):
        channel.add_conversation(6)


@patch('erdos.channel.Channel.start_event_loop')
@patch('threading.Thread')
def test__init_event_loop__(Thread, start_event_loop, channel):
    """Test __init_event_loop__ method of Channel class

    Args:
    channel (Channel): Channel object
    """

    loop = channel.__init_event_loop__()

    assert isinstance(loop, asyncio.AbstractEventLoop)
    # Ensure thread is created with the correct arguments
    Thread.assert_called_with(
        target=start_event_loop, args=(
            loop,), daemon=True)
