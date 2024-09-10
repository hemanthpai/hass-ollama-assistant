"""Helper functions for Ollama."""

from homeassistant.components.conversation import DOMAIN as CONVERSATION_DOMAIN
from homeassistant.components.homeassistant.exposed_entities import async_should_expose
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry, area_registry

from .const import ASSISTANT_ROLE, NAME_KEY, ROLE_KEY, SYSTEM_ROLE, CONTENT_KEY, TOOL_CALLS_KEY, TOOL_ROLE, USER_ROLE


def get_exposed_entities(hass: HomeAssistant) -> list[dict]:
    """Return exposed entities grouped by area."""
    hass_entity = entity_registry.async_get(hass)
    hass_area = area_registry.async_get(hass)
    exposed_entities: dict = {"scenes": [], "scripts": [], "automations": [], }

    for state in hass.states.async_all():
        if async_should_expose(hass, CONVERSATION_DOMAIN, state.entity_id):

            if state.domain == "scene":
                exposed_entities["scenes"].append({
                    "entity_id": state.entity_id,
                    "name": state.name,
                })
            elif state.domain == "script":
                exposed_entities["scripts"].append({
                    "entity_id": state.entity_id,
                    "name": state.name,
                })
            elif state.domain == "automation":
                exposed_entities["automations"].append({
                    "entity_id": state.entity_id,
                    "name": state.name,
                    "state": state.state,
                })
            else:
                entity = hass_entity.async_get(state.entity_id)
                area = hass_area.async_get_area(
                    entity.area_id) if entity and entity.area_id else None
                area_name = area.name if area else "No Area"

                if area_name not in exposed_entities:
                    exposed_entities[area_name] = []

                exposed_entities[area_name].append({
                    "entity_id": state.entity_id,
                    "name": state.name,
                    "state": state.state,
                    "attributes": state.attributes,
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
