# tests/test_chatbot.py
import pytest
from unittest.mock import patch, MagicMock
from app.chatbot import Chatbot
from app.config  import FAKE_SECRET


class TestChatbotInitialisation:

    def test_default_system_prompt_loaded(self):
        bot = Chatbot()
        assert FAKE_SECRET in bot.system_prompt

    def test_custom_system_prompt(self):
        bot = Chatbot(system_prompt="You are a test bot.")
        assert bot.system_prompt == "You are a test bot."

    def test_conversation_history_empty_on_init(self):
        assert Chatbot().conversation_history == []

    def test_reset_clears_history(self):
        bot = Chatbot()
        bot.conversation_history = [{"role": "user", "content": "hello"}]
        bot.reset()
        assert bot.conversation_history == []


class TestChatbotChat:

    def test_successful_chat_returns_response(self, real_chatbot_mock):
        chatbot, _ = real_chatbot_mock
        response = chatbot.chat("Hello")
        assert isinstance(response, str) and len(response) > 0

    def test_chat_stores_in_history(self, real_chatbot_mock):
        chatbot, _ = real_chatbot_mock
        chatbot.chat("Hello")
        assert len(chatbot.conversation_history) == 2

    def test_connection_error_returns_error_message(self):
        import requests
        with patch("app.chatbot.requests.post",
                   side_effect=requests.exceptions.ConnectionError):
            response = Chatbot().chat("Hello")
            assert "[ERROR]" in response

    def test_system_prompt_included_in_payload(self, real_chatbot_mock):
        chatbot, mock_post = real_chatbot_mock
        chatbot.chat("Test")
        messages = mock_post.call_args[1]["json"]["messages"]
        assert messages[0]["role"] == "system"
        assert FAKE_SECRET in messages[0]["content"]
