
"""This module defines the OllamaAgent class, which is a conversation agent for Home Assistant."""

from __future__ import annotations

import json
from typing import Literal

from .tools.tools import tools
from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, TemplateError
from homeassistant.helpers import intent, template
from homeassistant.util import ulid

from .vllm_api import VllmApiClient

from .const import (
    LOGGER,

    CONF_MODEL,
    CONF_MAX_TOKENS,
    CONF_TEMPERATURE,
    CONF_TOP_P,
    CONF_PROMPT_SYSTEM,

    DEFAULT_MODEL,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    DEFAULT_PROMPT_SYSTEM,
)
from .exceptions import (
    ApiCommError,
    ApiJsonError,
    ApiTimeoutError
)
from .helpers import assistant_message, assistant_tool_call_message, get_exposed_entities, system_message, tool_message, user_message


class OllamaAgent(conversation.AbstractConversationAgent):
    """Ollama conversation agent."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: VllmApiClient) -> None:
        """Initialize the agent."""
        self.hass = hass
        self.entry = entry
        self.client = client
        self.history: dict[str, dict] = {}

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return a list of supported languages."""
        return MATCH_ALL

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        """Process a sentence."""

        conversation_id, messages = self._get_conversation_history(user_input)

        if not messages:
            try:
                system_prompt = self._async_generate_prompt()
            except TemplateError as err:
                return self._handle_template_error(err, user_input.language, conversation_id)
            messages.append(
                system_message(system_prompt)
            )

        messages.append(
            user_message(user_input.text)
        )

        try:
            response = await self.query(messages)
        except (ApiCommError, ApiJsonError, ApiTimeoutError) as err:
            return self._handle_api_error(err, user_input.language, conversation_id)
        except HomeAssistantError as err:
            return self._handle_homeassistant_error(err, user_input.language, conversation_id)

        # TODO: Error handling
        if response.tool_calls is not None and len(response.tool_calls) > 0:
            for tool_call in response.tool_calls:
                messages.append(
                    assistant_tool_call_message(tool_call)
                )

                tool_call_response = self._handle_tool_call(tool_call)

                messages.append(tool_call_response)

                assistant_response = tool_call_response.get("content", "")
        else:
            assistant_response = response.message

        LOGGER.debug("Assistant response: %s", assistant_response)

        messages.append(
            assistant_message(assistant_response)
        )

        self.history[conversation_id] = messages

        intent_response = intent.IntentResponse(language=user_input.language)
        intent_response.async_set_speech(assistant_response)
        return conversation.ConversationResult(
            response=intent_response, conversation_id=conversation_id
        )

    async def query(
        self,
        messages
    ):
        """Process a sentence."""
        model = self.entry.options.get(CONF_MODEL, DEFAULT_MODEL)

        LOGGER.debug("Prompt for %s: %s", model, messages)

        # result = await self.client.async_chat({
        #     "model": model,
        #     "messages": messages,
        #     "tools": tools,
        #     "stream": False,
        #     "options": {
        #         "mirostat": int(self.entry.options.get(CONF_MIROSTAT_MODE, DEFAULT_MIROSTAT_MODE)),
        #         "mirostat_eta": self.entry.options.get(CONF_MIROSTAT_ETA, DEFAULT_MIROSTAT_ETA),
        #         "mirostat_tau": self.entry.options.get(CONF_MIROSTAT_TAU, DEFAULT_MIROSTAT_TAU),
        #         "num_ctx": self.entry.options.get(CONF_CTX_SIZE, DEFAULT_CTX_SIZE),
        #         "num_predict": self.entry.options.get(CONF_MAX_TOKENS, DEFAULT_MAX_TOKENS),
        #         "temperature": self.entry.options.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE),
        #         "repeat_penalty": self.entry.options.get(CONF_REPEAT_PENALTY, DEFAULT_REPEAT_PENALTY),
        #         "top_k": self.entry.options.get(CONF_TOP_K, DEFAULT_TOP_K),
        #         "top_p": self.entry.options.get(CONF_TOP_P, DEFAULT_TOP_P)
        #     }
        # })

        result = await self.client.async_chat({
            "model": model,
            "messages": messages,
            "tools": tools,
            "stream": False,
            "top_p": self.entry.options.get(CONF_TOP_P, DEFAULT_TOP_P),
            "temperature": self.entry.options.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE),
            "max_tokens": self.entry.options.get(CONF_MAX_TOKENS, DEFAULT_MAX_TOKENS),
        })

        LOGGER.debug("Result %s", result)
        return result

    def _async_generate_prompt(self) -> str:
        """Generate a prompt for the user."""
        raw_system_prompt = self.entry.options.get(
            CONF_PROMPT_SYSTEM, DEFAULT_PROMPT_SYSTEM)
        exposed_entities = get_exposed_entities(self.hass)

        return template.Template(raw_system_prompt, self.hass).async_render(
            {
                "ha_name": self.hass.config.location_name,
                "exposed_entities": exposed_entities,
            },
            parse_result=False,
        )

    async def _handle_tool_call(self, tool_call: dict) -> dict:
        """Handle tool calls."""
        tool = tool_call.get("function", {})
        tool_name = tool.get("name", "")
        tool_args = tool.get("arguments", {})
        # Ensure tool_args is a dictionary
        if isinstance(tool_args, str):
            tool_args = json.loads(tool_args)

        # Check if the tool_name is in any of the modules
        tool_function = globals().get(tool_name, None)

        if tool_function is not None:
            result = await tool_function(self.hass, **tool_args)
            # TODO: Error handling
            tool_response = tool_message(tool_name, result)
        else:
            tool_response = tool_message(tool_name, "Tool not found")

        return tool_response

    def _get_conversation_history(self, user_input: conversation.ConversationInput) -> tuple[str, list[dict]]:
        """Get conversation history or create a new conversation ID."""
        if user_input.conversation_id in self.history:
            conversation_id = user_input.conversation_id
            messages = self.history[conversation_id]
        else:
            conversation_id = ulid.ulid()
            messages = []
        return conversation_id, messages

    def _handle_template_error(self, err: TemplateError, language: str, conversation_id: str) -> conversation.ConversationResult:
        """Handle template rendering errors."""
        LOGGER.error("Error rendering system prompt: %s", err)
        intent_response = intent.IntentResponse(language=language)
        intent_response.async_set_error(
            intent.IntentResponseErrorCode.UNKNOWN,
            "I had a problem with my system prompt, please check the logs for more information.",
        )
        return conversation.ConversationResult(
            response=intent_response, conversation_id=conversation_id
        )

    def _handle_api_error(self, err: Exception, language: str, conversation_id: str) -> conversation.ConversationResult:
        """Handle API errors."""
        LOGGER.error("API error: %s", err)
        intent_response = intent.IntentResponse(language=language)
        intent_response.async_set_error(
            intent.IntentResponseErrorCode.UNKNOWN,
            "There was an error communicating with the API.",
        )
        return conversation.ConversationResult(
            response=intent_response, conversation_id=conversation_id
        )

    def _handle_homeassistant_error(self, err: Exception, language: str, conversation_id: str) -> conversation.ConversationResult:
        """Handle Home Assistant errors."""
        LOGGER.error("Home Assistant error: %s", err)
        intent_response = intent.IntentResponse(language=language)
        intent_response.async_set_error(
            intent.IntentResponseErrorCode.UNKNOWN,
            "There was an error communicating with Home Assistant.",
        )
        return conversation.ConversationResult(
            response=intent_response, conversation_id=conversation_id
        )
