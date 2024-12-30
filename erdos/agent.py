from langchain_community.chat_models import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.prompts.prompt import PromptTemplate
from langchain_openai import ChatOpenAI
import asyncio
import json


class Agent:

    LLM_API_TIMEOUT = 60 * 3

    # Singleton instance
    instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super(Agent, cls).__new__(cls)
        return cls.instance

    def __init__(self, llm_api_key: str):
        if hasattr(self, '_init') and self._init:
            return
        self.llm = self.__initialize_llm__(llm_api_key)
        self.history = {}
        self._init = True

    def get_session_history(self, conversation_id: str) -> ChatMessageHistory:
        """Get conversation history based on conversation_id. Helper for RunnableWithMessageHistory

        Args:
            conversation_id (str): conversation id

        Returns:
            ChatMessageHistory: conversation history
        """
        if conversation_id not in self.history:
            self.history[conversation_id] = ChatMessageHistory()
        return self.history[conversation_id]

    def add_to_session_history(self, conversation_id: str,
                               conversation_history: ChatMessageHistory):
        """Adding conversation history to agent's session history

        Args:
            conversation_id (str): conversation id
            message (ChatMessageHistory): conversation history
        """
        conversation_history = ChatMessageHistory.model_validate(
            json.loads(conversation_history))
        self.history[conversation_id] = conversation_history

    def __initialize_llm__(
            self, llm_api_key: str) -> RunnableWithMessageHistory:
        """Initialise LLM chain with custom prompt

        Returns:
            runnable_with_history (RunnableWithMessageHistory): LLM chain object
        """

        # Temperature set to 0 to get deterministic responses, since it's a math
        # assistant
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0,
            openai_api_key=llm_api_key)

        # Define a custom prompt
        prompt = PromptTemplate(
            input_variables=["history", "input"],
            template=(
                """You are a helpful assistant.
                You specialize in assisting with basic math operations, so that users
                can ask various math-related questions and receive answers.
                If the question is too complex, break it down into a series of intermediate steps.
                Here is the conversation so far:\n
                {history}\n
                User: {input}\n
                Assistant:"""
            ),
        )

        runnable = prompt | llm  # Connect the prompt to the LLm chain

        runnable_with_history = RunnableWithMessageHistory(
            runnable,
            get_session_history=self.get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        )

        # Define a conversation chain with custom prompt
        return runnable_with_history

    async def send_message(self, conversation_id: int, message: str) -> str:
        """Send message to the LLM chain, with conversation_id identifying a conversation as context

        Args:
            conversation_id (int): conversation id
            message (str): prompt

        Returns:
            responses.content: LLM chain response
        """
        try:
            response = await asyncio.wait_for(self.llm.ainvoke(
                {"input": message},
                config={"configurable": {"session_id": conversation_id}},
            ), timeout=Agent.LLM_API_TIMEOUT)

        except Exception as e:
            return "LLM API is not responsive at the moment. Following error occured: {e}"
        return response.content

    def get_messages(self, conversation_id: int, stringified: bool = False):
        """Return the conversation history based on the conversation_id

        Args:
            conversation_id (int): id of the conversation

        Returns:
            messages: conversation history
        """
        messages = self.get_session_history(conversation_id)
        return self.stringify_messages(messages) if stringified else messages

    @staticmethod
    def stringify_messages(message_history: ChatMessageHistory) -> str:
        if not message_history or not message_history.messages:
            return ""
        return "\n".join(
            [f"{msg.type.capitalize()}: {msg.content}" for msg in message_history.messages])
