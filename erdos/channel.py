import threading
import asyncio
from .conversation import Conversation


class Channel:

    def __init__(self, name: str, llm_api_key: str,
                 max_conversations: int = 500):
        """
        Args:
            name (str):
            is_closed (bool, optional): Defaults to False.
            max_conversations (int, optional): maximum allowed concurrent conversations. Defaults to 500.
        """
        self._name = name
        self.max_conversations = max_conversations
        self.event_loop = self.__init_event_loop__()
        self.event_loop_thread = None
        self.conversations = {}
        self.llm_api_key = llm_api_key

    @staticmethod
    def start_event_loop(loop):
        """Start the event loop

        Args:
            loop (asyncio.AbstractEventLoop): event loop to handle LLM calls
        """
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def __init_event_loop__(self):
        """Initialize event loop for the channel to run in a separate thread

        Returns:
            Conversation: conversation object
        """
        loop = asyncio.new_event_loop()
        # Start the event loop in a separate thread, make thread daemonic to allow
        # for clean exit
        thread = threading.Thread(
            target=self.start_event_loop, args=(
                loop,), daemon=True)
        thread.start()

        return loop

    def add_conversation(self, conversation_id: int = None) -> Conversation:
        """Add a new conversation to the channel

        Args:
            conversation_id (int, optional): Defaults to None.
        Returns:
            Conversation: conversation object
        """

        # Ensure conversation_id is unique
        if conversation_id in self.conversations:
            raise ValueError(
                f"Conversation with id {conversation_id} already exists")

        # Ensure maximum number of conversations is not exceeded
        if len(self.conversations) >= self.max_conversations:
            raise ValueError(
                f"Maximum number of conversations reached: {self.max_conversations}")

        # Get the next available conversation_id
        new_conversation_id = 1 if not self.conversations else max(
            self.conversations.keys(), default=0) + 1
        # Use the provided conversation_id or the next available id if not
        # provided
        conversation_id = conversation_id or new_conversation_id
        self.conversations[conversation_id] = Conversation(
            conversation_id, self.event_loop, self.llm_api_key)
        return self.conversations[conversation_id]

    def get_conversation(self, conversation_id) -> Conversation:
        """Get specific conversation

        Args:
            conversation_id (int): id of the conversation

        Returns:
            Conversation: conversation object
        """
        return self.conversation.get(conversation_id)

    def get_conversations(self) -> list[Conversation]:
        """Get all conversations

        Returns:
            list[Conversation]: all conversations within channel
        """
        return self.conversations
