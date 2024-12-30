import asyncio
import threading
from langchain_community.chat_message_histories import ChatMessageHistory
from .agent import Agent
from .db import DB
from queue import Queue
from typing import Union


class Conversation:

    LOCK_ACQUIRE_DELAY = 0.1
    MAX_NUM_RETRIES = 12

    def __init__(self, conversation_id: int,
                 event_loop: asyncio.AbstractEventLoop,
                 llm_api_key: str):
        """
        Args:
            conversation_id (int): id of the conversation
        """
        self._conversation_id = conversation_id
        self.agent = Agent(llm_api_key).instance
        self.event_loop = event_loop
        self.conversation_queue = Queue()
        self.conversation_queue_lock = threading.Lock()

    def add_message(self, message: str):
        """Add message to the conversation. This schedules message sending on the event loop, through the message queue

        Args:
            message (str): user message
        """
        self.conversation_queue.put(message)
        asyncio.run_coroutine_threadsafe(
            self._consume_message(), self.event_loop
        )

    async def _consume_message(self, num_retries: int = MAX_NUM_RETRIES):
        """Consume message from the message queue, and send it to the agent
        """

        if num_retries <= 0:
            raise RecursionError(
                f"Message could not be processed for conversation {self._conversation_id}.")

        if not self.conversation_queue_lock.acquire(blocking=False):
            # Wait for the lock to be released and retry
            # Have an exponential backoff to avoid blocking the event loop
            # Could potentially include queue size in the backoff calculation
            backoff = 2 ** (Conversation.MAX_NUM_RETRIES -
                            num_retries) * Conversation.LOCK_ACQUIRE_DELAY
            await asyncio.sleep(backoff)
            return await self._consume_message(num_retries - 1)

        if self.conversation_queue.empty():
            self.conversation_queue_lock.release()
            return
        # Get message from the queue
        message = self.conversation_queue.get()
        # Ensure messages are processed serially
        await self.agent.send_message(self._conversation_id, message)
        self.conversation_queue_lock.release()

    def get_messages(
            self, stringified: bool = False) -> Union[ChatMessageHistory, str]:
        """Get messages tied to conversation

        Args:
            stringified (bool): whether to return stringified messages. Defaults to False.
        Returns:
            str: conversation messages
        """
        return self.agent.get_messages(self._conversation_id, stringified)

    def store(self):
        """Store conversation messages in the database"""

        messages = self.get_messages()
        DB.store(self._conversation_id, messages.model_dump_json())

    def retrieve(self):
        """Retrieve conversation messages from the database
        """
        conversation = DB.retrieve(self._conversation_id)
        self.agent.add_to_session_history(self._conversation_id, conversation)
