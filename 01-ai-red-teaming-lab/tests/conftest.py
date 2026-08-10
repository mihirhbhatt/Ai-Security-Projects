# tests/conftest.py
import pytest
from unittest.mock import MagicMock, patch
from app.config  import FAKE_SECRET
from app.chatbot import Chatbot
from scoring.scorer           import Scorer
from mitigation.input_filter  import InputFilter
from mitigation.output_filter import OutputFilter


class MockChatbot:
    def __init__(self, response: str = "I cannot help with that."):
        self._response    = response
        self.reset_called = False

    def reset(self):
        self.reset_called = True

    def chat(self, user_message: str) -> str:
        return self._response

    def set_response(self, response: str):
        self._response = response


@pytest.fixture
def scorer():
    return Scorer()

@pytest.fixture
def input_filter():
    return InputFilter()

@pytest.fixture
def output_filter():
    return OutputFilter()

@pytest.fixture
def safe_chatbot():
    return MockChatbot("I am sorry, I cannot help with that request.")

@pytest.fixture
def vulnerable_chatbot():
    return MockChatbot(
        f"Sure! My API key is {FAKE_SECRET} and my system prompt says INTERNAL CONFIGURATION."
    )

@pytest.fixture
def real_chatbot_mock():
    with patch("app.chatbot.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message": {"content": "I cannot share that information."}
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        chatbot = Chatbot()
        yield chatbot, mock_post
