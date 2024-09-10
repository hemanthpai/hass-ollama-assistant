"""This module provides the OpenAIAgent class for handling conversations with OpenAI."""

from typing import Literal

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, TemplateError
from homeassistant.helpers import intent, template
from homeassistant.util import ulid

from openai import OpenAI

from .const import (
    LOGGER,

    CONF_MODEL,
    CONF_TEMPERATURE,
    CONF_TOP_P,
    CONF_PROMPT_SYSTEM,

    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    DEFAULT_PROMPT_SYSTEM
)

from .helpers import get_exposed_entities

class OpenAIAgent(conversation.AbstractConversationAgent):
    """Agent to handle a conversation with OpenAI."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: OpenAI) -> None:
        """Initialize the agent."""
        self.hass = hass
        self.entry = entry
        self.client = client
        self.conversation_id = None
        self.assistant = self._async_create_assistant(client)
        self.assistant_thread = self.client.beta.threads.create()

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return a list of supported languages."""
        return MATCH_ALL

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        """Process a text command."""

        if user_input.conversation_id != self.conversation_id:
            self.conversation_id = ulid.ulid()

        self.client.beta.threads.messages.create(
            thread=self.assistant_thread.id,
            role="user",
            content=user_input.text,
        )

        run = self.client.beta.threads.runs.create_and_poll(
            thread=self.assistant_thread.id,
            model=self.assistant.model,
        )

        if run.status == "completed":
            messages = self.client.beta.threads.messages.list(thread=self.assistant_thread.id)
            assert messages[-1].content[0].type == "assistant"
            assistant_response = messages[-1].content[0].text.value

            intent_response = intent.IntentResponse(language=user_input.language)
            intent_response.async_set_speech(assistant_response)
            return conversation.ConversationResult(
               intent_response=intent_response,
               conversation_id=self.conversation_id,
            )



    def _async_generate_prompt(self) -> str:
        """Generate a prompt for the user."""
        raw_prompt = self.entry.options.get(CONF_PROMPT_SYSTEM, DEFAULT_PROMPT_SYSTEM)
        exposed_entities = get_exposed_entities(self.hass)

        return template.Template(raw_prompt, self.hass).async_render(
            {
                "ha_name": self.hass.config.location_name,
                "exposed_entities": exposed_entities,
            },
            parse_result=False,
        )

    def _async_create_assistant(self, client: OpenAI):
        """Create an assistant."""

        model = self.entry.options.get(CONF_MODEL, DEFAULT_MODEL)

        try:
            system_prompt = self._async_generate_prompt()
        except TemplateError as exception:
            LOGGER.error("Error rendering system prompt: %s", exception)
            raise HomeAssistantError("Error rendering system prompt") from exception

        return client.beta.assistants.create(
            name="Home Assistant",
            instructions=system_prompt,
            model=model,
            temperature=self.entry.options.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE),
            top_p=self.entry.options.get(CONF_TOP_P, DEFAULT_TOP_P),
        )
