"""Helper functions for Ollama."""

from homeassistant.components.conversation import DOMAIN as CONVERSATION_DOMAIN
from homeassistant.components.homeassistant.exposed_entities import async_should_expose
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry

from .const import ASSISTANT_ROLE, NAME_KEY, ROLE_KEY, SYSTEM_ROLE, CONTENT_KEY, TOOL_CALLS_KEY, TOOL_ROLE, USER_ROLE

def get_exposed_entities(hass: HomeAssistant) -> list[dict]:
    """Return exposed entities."""
    hass_entity = entity_registry.async_get(hass)
    exposed_entities:list[dict] = []

    for state in hass.states.async_all():
        if async_should_expose(hass, CONVERSATION_DOMAIN, state.entity_id):
            entity = hass_entity.async_get(state.entity_id)
            exposed_entities.append({
                "entity_id": state.entity_id,
                "name": state.name,
                "state": state.state,
                "aliases": entity.aliases if entity else [],
            })

    return exposed_entities

def system_message(system_prompt: str) -> dict:
    """Generate a system message."""
    return {
        ROLE_KEY: SYSTEM_ROLE,
        CONTENT_KEY: system_prompt,
    }

def user_message(user_input: str) -> dict:
    """Generate a user message."""
    return {
        ROLE_KEY: USER_ROLE,
        CONTENT_KEY: user_input,
    }

def assistant_message(assistant_response: str) -> dict:
    """Generate an assistant message."""
    return {
        ROLE_KEY: ASSISTANT_ROLE,
        CONTENT_KEY: assistant_response,
    }

def tool_message(tool_name: str, tool_response: str) -> dict:
    """Generate a tool message."""
    return {
        ROLE_KEY: TOOL_ROLE,
        NAME_KEY: tool_name,
        CONTENT_KEY: tool_response,
    }

def assistant_tool_call_message(tool_call: dict) -> dict:
    """Generate an assistant tool call message."""
    return {
        ROLE_KEY: ASSISTANT_ROLE,
        TOOL_CALLS_KEY: [tool_call],
    }
