import pytest
from unittest.mock import patch
from erdos.agent import Agent
from langchain.schema.runnable import Runnable
from langchain_core.runnables.history import RunnableWithMessageHistory


@pytest.fixture
def agent():
    agent = Agent('1').instance
    yield agent


@patch('erdos.agent.Agent.get_session_history')
def test__initialize_llm__(get_session_history, agent):
    """Test __initialize_llm__ method of Agent class
    """

    runnable = agent.__initialize_llm__('1')
    # Ensure the returned object is a RunnableWithMessageHistory object
    assert isinstance(runnable, RunnableWithMessageHistory)
    # Ensure the runnable session getter is the same as the agent's session
    # getter
    assert runnable.get_session_history == get_session_history
