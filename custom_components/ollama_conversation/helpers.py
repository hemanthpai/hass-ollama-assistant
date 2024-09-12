"""Helper functions for Ollama."""

from datetime import datetime
from homeassistant.components.conversation import DOMAIN as CONVERSATION_DOMAIN
from homeassistant.components.homeassistant.exposed_entities import async_should_expose
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry, area_registry

from .const import ASSISTANT_ROLE, NAME_KEY, ROLE_KEY, SYSTEM_ROLE, CONTENT_KEY, TOOL_CALL_ID_KEY, TOOL_CALLS_KEY, TOOL_ROLE, USER_ROLE


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


def tool_message(tool_call_id: str, tool_name: str, tool_response: str) -> dict:
    """Generate a tool message."""
    return {
        ROLE_KEY: TOOL_ROLE,
        NAME_KEY: tool_name,
        CONTENT_KEY: tool_response,
        TOOL_CALL_ID_KEY: tool_call_id,
    }


def assistant_tool_call_message(tool_call: dict) -> dict:
    """Generate an assistant tool call message."""
    return {
        ROLE_KEY: ASSISTANT_ROLE,
        TOOL_CALLS_KEY: [tool_call],
    }


def generate_available_time_slots_from_calendar_events(events: list[dict], start_date_time: str, end_date_time: str) -> dict:
    """Generate available time slots from calendar events."""
    # Convert event times to datetime objects and sort by start time
    events = [
        {
            "start": datetime.fromisoformat(event["start"]),
            "end": datetime.fromisoformat(event["end"]),
            "summary": event["summary"]
        }
        for event in events
    ]
    events.sort(key=lambda x: x["start"])

    # Convert start and end date times to datetime objects
    start_dt = datetime.strptime(start_date_time, '%Y-%m-%d %H:%M:%S')
    end_dt = datetime.strptime(end_date_time, '%Y-%m-%d %H:%M:%S')

    # Generate available time slots
    available_time_slots = []

    current_time = start_dt

    for event in events:
        event_start_dt = event["start"]

        if event_start_dt.tzinfo is not None:
            # Convert input dates to the same timezone as the event
            start_dt = start_dt.replace(tzinfo=event_start_dt.tzinfo)
            end_dt = end_dt.replace(tzinfo=event_start_dt.tzinfo)
            current_time = current_time.replace(tzinfo=event_start_dt.tzinfo)

        if current_time < event["start"]:
            available_time_slots.append({
                "start": current_time.strftime('%Y-%m-%d %H:%M:%S'),
                "end": event["start"].strftime('%Y-%m-%d %H:%M:%S')
            })
        current_time = max(current_time, event["end"])

    if current_time < end_dt:
        available_time_slots.append({
            "start": current_time.strftime('%Y-%m-%d %H:%M:%S'),
            "end": end_dt.strftime('%Y-%m-%d %H:%M:%S')
        })

    return {"open_slots": available_time_slots}
