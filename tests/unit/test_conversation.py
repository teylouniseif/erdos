import asyncio
import pytest
from unittest.mock import patch, Mock, AsyncMock
from erdos.conversation import Conversation
from queue import Queue


@pytest.fixture
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def conversation():
    with patch("erdos.agent.Agent.instance") as agent:
        agent.return_value.send_message = AsyncMock()
        conversation = Conversation(1, event_loop, '1')
        conversation.agent = agent.return_value
        yield conversation


@patch("asyncio.run_coroutine_threadsafe")
def test_add_message(mock_run_threadsafe, conversation):
    """Test add_message method of Conversation class

    Args:
        mock_run_threadsafe (asyncio.run_coroutine_threadsafe): thread safe coroutine runner
        conversation (Conversation): Conversation object
    """

    _consume_message_mock = Mock()
    conversation._consume_message = _consume_message_mock

    conversation.add_message("What is 2+2?")

    # Ensure the coroutine is scheduled on the event loop
    mock_run_threadsafe.assert_called_once()

    called_coroutine = mock_run_threadsafe.call_args[0][0]

    # Ensure the coroutine scheduled matches the mocked _consume_message
    assert called_coroutine.cr_code is conversation._consume_message().cr_code

    # Ensure the event loop is the same as the conversation's event loop
    called_event_loop = mock_run_threadsafe.call_args[0][1]
    assert called_event_loop == conversation.event_loop


@pytest.mark.asyncio(loop_scope="module")
async def test__consume_message(conversation):
    """Test _consume_message method of Conversation class

    Args:
        conversation (Conversation): Conversation object
    """

    conversation.conversation_queue = Queue()
    conversation.conversation_queue.put("What is 2+2?")
    await conversation._consume_message()
    # Ensure agent.send_message is called with the correct arguments
    conversation.agent.send_message.assert_called_once_with(
        conversation._conversation_id, "What is 2+2?")

    conversation.conversation_queue.put("What is 3+3?")
    conversation.conversation_queue_lock.acquire()
    # Ensure agent.send_message is not called since lock not acquired

    lock_acquire_delay = Conversation.LOCK_ACQUIRE_DELAY
    Conversation.LOCK_ACQUIRE_DELAY = 0
    try:
        await conversation._consume_message()
    except Exception as e:
        assert isinstance(e, RecursionError)
    Conversation.LOCK_ACQUIRE_DELAY = lock_acquire_delay

    # Ensure agent.send_message is called with the correct arguments after
    # lock is released
    conversation.conversation_queue_lock.release()
    await conversation._consume_message()
    conversation.agent.send_message.assert_called_with(
        conversation._conversation_id, "What is 3+3?")


def test_get_messages(conversation):
    """Test get_messages method of Conversation class

    Args:
        conversation (Conversation): conversation object
    """
    conversation.get_messages()
    conversation.agent.get_messages.assert_called_once()
