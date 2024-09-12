"""This module provides tools for interacting with Home Assistant entities."""

from datetime import datetime
from enum import Enum

from .json_schema import get_json_schema

from .const import LOGGER, TOOL_DOES_NOT_EXIST

from .hass import HomeAssistantService, HomeAssistantServiceResult


class MediaAction(Enum):
    """An enumeration representing the actions that can be performed on a media player."""

    PLAY = "media_play"
    PAUSE = "media_pause"
    STOP = "media_stop"
    NEXT = "media_next_track"
    PREVIOUS = "media_previous_track"
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"
    VOLUME_MUTE = "volume_mute"
    SHUFFLE = "shuffle_set"


class HVACMode(Enum):
    """An enumeration representing the HVAC modes for climate devices."""

    OFF = "off"
    HEAT = "heat"
    COOL = "cool"
    AUTO = "auto"
    HEAT_COOL = "heat_cool"
    FAN_ONLY = "fan_only"


class PresetMode(Enum):
    """An enumeration representing the preset modes for climate devices."""

    HOME = "home"
    AWAY = "away"
    ECO = "eco"
    AUTO = "auto"


class FanMode(Enum):
    """An enumeration representing the fan modes for climate devices."""

    ON_LOW = "On Low"
    ON_HIGH = "On High"
    AUTO_LOW = "Auto Low"
    AUTO_HIGH = "Auto High"
    OFF = "Off"


class VacuumAction(Enum):
    """An enumeration representing the actions that can be performed on a vacuum."""

    START = "start"
    STOP = "stop"
    PAUSE = "pause"
    RETURN_TO_BASE = "return_to_base"


class FanAction(Enum):
    """An enumeration representing the actions that can be performed on a fan."""

    INCREASE_SPEED = "increase_speed"
    DECREASE_SPEED = "decrease_speed"


SUPPORTED_DOMAINS = {
    "hass_turn_on": ["light", "switch", "fan", "climate", "media_player", "automation", "script", "scene"],
    "hass_turn_off": ["light", "switch", "fan", "climate", "media_player", "automation", "script"],
    "hass_toggle": ["light", "switch", "fan", "climate", "media_player", "lock", "cover", "automation", "script"],
    "hass_open": ["cover"],
    "hass_close": ["cover"],
    "hass_set_temperature": ["climate"],
    "hass_set_humidity": ["climate"],
    "hass_set_fan_mode": ["climate"],
    "hass_set_hvac_mode": ["climate"],
    "hass_set_preset_mode": ["climate"],
    "hass_lock": ["lock"],
    "hass_unlock": ["lock"],
    "hass_vacuum_control": ["vacuum"],
    "hass_fan_control": ["fan"],
    "hass_media_control": ["media_player"],
    "hass_get_agenda": ["calendar"],
    "hass_get_calendar_availability": ["calendar"],
    "hass_get_calendar_events": ["calendar"],
}


class ToolCallResult:
    """Result of a tool call."""

    def __init__(self):
        """Initialize the result."""
        self.success = False
        self.errored_entity_ids = []
        self.missing_domain_entity_ids = []
        self.incorrect_domain_entity_ids = []
        self.domain_not_supported_entity_ids = []

    def __str__(self):
        """Return a string representation of the result."""
        return_string = ""
        if self.success:
            return_string = "Success"
        else:
            return_string = "Failure"
        if len(self.errored_entity_ids) > 0:
            return_string += f", an error occurred for the following entity IDs: {
                ', '.join(self.errored_entity_ids)}"
        if len(self.missing_domain_entity_ids) > 0:
            return_string += f", the following entity IDs are missing a valid domain: {
                ', '.join(self.missing_domain_entity_ids)}"
        if len(self.incorrect_domain_entity_ids) > 0:
            return_string += f", the following entity IDs have an incorrect domain: {
                ', '.join(self.incorrect_domain_entity_ids)}"
        if len(self.domain_not_supported_entity_ids) > 0:
            return_string += f", the following entity IDs have a domain that is not supported by this tool: {
                ', '.join(self.domain_not_supported_entity_ids)}"

        return return_string

    def add_errored_entity_id(self, entity_id: list[str]):
        """Add an entity ID that encountered an error."""
        self.errored_entity_ids.extend(entity_id)

    def add_missing_domain_entity_id(self, entity_id: list[str]):
        """Add an entity ID that is missing a valid domain."""
        self.missing_domain_entity_ids.extend(entity_id)

    def add_incorrect_domain_entity_id(self, entity_id: list[str]):
        """Add an entity ID that has an incorrect domain."""
        self.incorrect_domain_entity_ids.extend(entity_id)

    def add_domain_not_supported_entity_id(self, entity_id: list[str]):
        """Add an entity ID that has a domain that is not supported by this tool."""
        self.domain_not_supported_entity_ids.extend(entity_id)


class ToolCallSuggestions:
    """Suggestions for tool calls based on entity IDs."""

    def __init__(self):
        """Initialize the suggestions."""
        self.suggested_tool_calls = []
        self.invalid_entity_ids = []

    def __str__(self):
        """Return a string representation of the suggestions."""

        return_string = TOOL_DOES_NOT_EXIST

        if len(self.suggested_tool_calls) > 0:
            return_string += "\nSuggestions for tools based on the specified entity IDs:"

            for tool_call in self.suggested_tool_calls:
                return_string += f"\n{tool_call}"

        if len(self.invalid_entity_ids) > 0:
            return_string += f"\nAlso, the following entity IDs are invalid: {
                ', '.join(self.invalid_entity_ids)}"
            return_string += ". Entity IDs must start with a valid domain followed by a period."

        return return_string

    def add_suggested_tool_call(self, tool_call: str):
        """Add a suggested tool call."""
        self.suggested_tool_calls.append(tool_call)

    def add_invalid_entity_id(self, entity_id: str):
        """Add an entity ID that is invalid."""
        self.invalid_entity_ids.extend(entity_id)


def validate_entity_ids(entity_ids: list[str], domain_entity_map: dict, tool_call_result: ToolCallResult, tool_name: str):
    """Validate the entity IDs in the 'entity_ids' parameter.

    Args:
        entity_ids: The entity IDs to validate.
        domain_entity_map: A dictionary to hold the mapping of entity IDs to their respective domains.
        tool_call_result: An instance of ToolCallResult to update with the results of validation.
        tool_name: The name of the tool making the validation call.

    """
    for entity_id in entity_ids:
        if "." not in entity_id:
            tool_call_result.add_missing_domain_entity_id([entity_id])
            continue

        domain = entity_id.split(".")[0]

        if domain not in SUPPORTED_DOMAINS[tool_name]:
            tool_call_result.add_domain_not_supported_entity_id([entity_id])
            continue

        if domain not in domain_entity_map:
            domain_entity_map[domain] = []
        domain_entity_map[domain].append(entity_id)


def process_service_call_results(service_call_results: list[HomeAssistantServiceResult], tool_call_result: ToolCallResult):
    """Process the results of service calls.

    Args:
        service_call_results: A list of HomeAssistantServiceResult objects to process.
        tool_call_result: An instance of ToolCallResult to update with the results of the service calls.

    """
    for result in service_call_results:
        if not result.success:
            tool_call_result.add_errored_entity_id(result.error)

    tool_call_result.success = all(
        result.success for result in service_call_results)


async def make_service_call(entity_ids: list[str], service: str, tool_name: str):
    """Make a service call to Home Assistant.

    Args:
        entity_ids: The entity IDs to call the service on.
        domain: The domain of the entities.
        service: The service to call.
        tool_name: The name of the tool making the service call.

    """

    domain_entity_map = {}
    service_call_results: list[HomeAssistantServiceResult] = []
    tool_call_result = ToolCallResult()

    validate_entity_ids(entity_ids, domain_entity_map,
                        tool_call_result, tool_name)

    for domain, ids in domain_entity_map.items():
        result = await HomeAssistantService.async_call_service(
            ids, domain, service)
        service_call_results.append(result)

    process_service_call_results(service_call_results, tool_call_result)

    return str(tool_call_result)


async def make_service_call_with_action(entity_id: str, action: str, tool_name: str):
    """Make a service call to Home Assistant.

    Args:
        entity_id: The entity ID to call the service on.
        domain: The domain of the entities.
        action: The action to perform on the entities.
        tool_name: The name of the tool making the service call.

    """

    tool_call_result = ToolCallResult()

    if "." not in entity_id:
        tool_call_result.add_missing_domain_entity_id([entity_id])
    else:
        domain = entity_id.split(".")[0]

        if domain not in SUPPORTED_DOMAINS[tool_name]:
            tool_call_result.add_domain_not_supported_entity_id([entity_id])
        else:
            result = await HomeAssistantService.async_call_service(
                [entity_id], domain, action)
            process_service_call_results([result], tool_call_result)

    return str(tool_call_result)


async def make_service_call_with_data(entity_id: str, service: str, data: dict, tool_name: str):
    """Make a service call to Home Assistant.

    Args:
        entity_id: The entity ID to call the service on.
        service: The service to call.
        data: The data to pass to the service.
        tool_name: The name of the tool making the service call.

    """

    tool_call_result = ToolCallResult()

    if "." not in entity_id:
        tool_call_result.add_missing_domain_entity_id([entity_id])
    else:
        domain = entity_id.split(".")[0]

        if domain not in SUPPORTED_DOMAINS[tool_name]:
            tool_call_result.add_domain_not_supported_entity_id([entity_id])
        else:
            result = await HomeAssistantService.async_call_service(
                [entity_id], domain, service, data)
            process_service_call_results([result], tool_call_result)

    return str(tool_call_result)


def suggest_tool_call(entity_ids: list[str] | str) -> ToolCallSuggestions:
    """Suggest a tool call based on the entity IDs provided in the 'entity_ids' parameter.

    Args:
        entity_ids: The entity IDs to suggest a tool call for.

    """
    if not isinstance(entity_ids, list) or not all(isinstance(id, str) for id in entity_ids) or not isinstance(entity_ids, str):
        raise ValueError("entity_ids must be a list of strings")
    if isinstance(entity_ids, list) and len(entity_ids) < 1:
        raise ValueError("entity_ids must contain at least one entity ID")

    tool_call_suggestions = ToolCallSuggestions()

    if isinstance(entity_ids, str):
        entity_ids = [entity_ids]

    domain_entity_map = {}
    for entity_id in entity_ids:
        if "." not in entity_id:
            tool_call_suggestions.add_invalid_entity_id(entity_id)
            continue

        domain = entity_id.split(".")[0]

        if domain not in domain_entity_map:
            domain_entity_map[domain] = []
        domain_entity_map[domain].append(entity_id)

    for domain, _ids in domain_entity_map.items():
        for tool_name, supported_domains in SUPPORTED_DOMAINS.items():
            if domain in supported_domains:
                tool_call_suggestions.add_suggested_tool_call(tool_name)

    return tool_call_suggestions


def validate_time_range(start_date: str, end_date: str):
    """Validate the time range specified in the 'start_time' and 'end_time' parameters.

    Args:
        start_date: The start time of the time range.
        end_date: The end time of the time range.

    """
    if not isinstance(start_date, str):
        raise TypeError("start_date must be a string")

    if not isinstance(end_date, str):
        raise TypeError("end_date must be a string")

    if start_date == "":
        raise ValueError("start_date must not be empty")

    if end_date == "":
        raise ValueError("end_date must not be empty")

    # Validate date format
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        raise ValueError(
            "start_date must be in the format 'YYYY-MM-DD HH:MM:SS'")

    try:
        end_dt = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        raise ValueError(
            "end_date must be in the format 'YYYY-MM-DD HH:MM:SS'")

    if start_dt > end_dt:
        raise ValueError("start_date must be before end_date")


async def hass_turn_on(entity_ids: list[str]):
    """Turn on the entities specified in the 'entity_ids' parameter.

    Supported entity types are: light, switch, fan, climate, media_player, automation, script, and scene.

    Args:
        entity_ids: The entity IDs of devices or entities that need to be turned on.

    """
    if not isinstance(entity_ids, list) or not all(isinstance(id, str) for id in entity_ids):
        raise ValueError("entity_ids must be a list of strings")
    if len(entity_ids) < 1:
        raise ValueError("entity_ids must contain at least one entity ID")

    LOGGER.debug(f"Turning on entities: {', '.join(entity_ids)}")

    result = await make_service_call(entity_ids, "turn_on", "hass_turn_on")

    return result


async def hass_turn_off(entity_ids: list[str]):
    """Turn off the entities specified in the 'entity_ids' parameter.

    Supported entity types are: light, switch, fan, climate, media_player, automation, and script.

    Args:
        entity_ids: The entity IDs of devices or entities that need to be turned off.

    """
    if not isinstance(entity_ids, list) or not all(isinstance(id, str) for id in entity_ids):
        raise ValueError("entity_ids must be a list of strings")
    if len(entity_ids) < 1:
        raise ValueError("entity_ids must contain at least one entity ID")

    LOGGER.debug(f"Turning off entities: {', '.join(entity_ids)}")

    result = await make_service_call(entity_ids, "turn_off", "hass_turn_off")

    return result


async def hass_toggle(entity_ids: list[str]):
    """Toggle the entities specified in the 'entity_ids' parameter.

    Supported entity types are: light, switch, fan, climate, media_player, lock, cover, automation, and script.

    Args:
        entity_ids: The entity IDs of devices or entities that need to be toggled.

    """
    if not isinstance(entity_ids, list) or not all(isinstance(id, str) for id in entity_ids):
        raise ValueError("entity_ids must be a list of strings")
    if len(entity_ids) < 1:
        raise ValueError("entity_ids must contain at least one entity ID")

    LOGGER.debug(f"Toggling entities: {', '.join(entity_ids)}")

    result = await make_service_call(entity_ids, "toggle", "hass_toggle")

    return result


async def hass_open(entity_ids: list[str]):
    """Open the entities specified in the 'entity_ids' parameter.

    Only supported for the cover entity type, such as garage doors or blinds.

    Args:
        entity_ids: The entity IDs of devices or entities that need to be opened.

    """
    if not isinstance(entity_ids, list) or not all(isinstance(id, str) for id in entity_ids):
        raise ValueError("entity_ids must be a list of strings")
    if len(entity_ids) < 1:
        raise ValueError("entity_ids must contain at least one entity ID")

    LOGGER.debug(f"Opening entities: {', '.join(entity_ids)}")

    result = await make_service_call(entity_ids, "open_cover", "hass_open")

    return result


async def hass_close(entity_ids: list[str]):
    """Close the entities specified in the 'entity_ids' parameter.

    Only supported for the cover entity type, such as garage doors or blinds.

    Args:
        entity_ids: The entity IDs of devices or entities that need to be closed.

    """
    if not isinstance(entity_ids, list) or not all(isinstance(id, str) for id in entity_ids):
        raise ValueError("entity_ids must be a list of strings")
    if len(entity_ids) < 1:
        raise ValueError("entity_ids must contain at least one entity ID")

    LOGGER.debug(f"Closing entities: {', '.join(entity_ids)}")

    result = await make_service_call(entity_ids, "close_cover", "hass_close")

    return result


async def hass_lock(entity_ids: list[str]):
    """Lock the entities specified in the 'entity_ids' parameter.

    Only supported for lock entities.

    Args:
        entity_ids: The entity IDs of locks that need to be locked.

    """

    if not isinstance(entity_ids, list) or not all(isinstance(id, str) for id in entity_ids):
        raise ValueError("entity_ids must be a list of strings")
    if len(entity_ids) < 1:
        raise ValueError("entity_ids must contain at least one entity ID")

    LOGGER.debug(f"Locking entities: {', '.join(entity_ids)}")

    result = await make_service_call(entity_ids, "lock", "hass_lock")

    return result


async def hass_unlock(entity_ids: list[str]):
    """Unlock the entities specified in the 'entity_ids' parameter.

    Only supported for lock entities.

    Args:
        entity_ids: The entity IDs of locks that need to be unlocked.

    """

    if not isinstance(entity_ids, list) or not all(isinstance(id, str) for id in entity_ids):
        raise ValueError("entity_ids must be a list of strings")
    if len(entity_ids) < 1:
        raise ValueError("entity_ids must contain at least one entity ID")

    LOGGER.debug(f"Unlocking entities: {', '.join(entity_ids)}")

    result = await make_service_call(entity_ids, "unlock", "hass_unlock")

    return result


async def hass_vacuum_control(entity_id: str, action: str):
    """Control the vacuum entity specified in the 'entity_id' parameter with the action specified in the 'action' parameter.

    Args:
        entity_id: A string containing the entity ID of the vacuum device that needs to be controlled.
        action: The action to perform on the vacuum (choices: ['start', 'stop', 'pause', 'return_to_base']).

    """

    if action not in [act.value for act in VacuumAction]:
        raise ValueError(
            "action must be one of the supported actions: 'start', 'stop', 'pause', 'return_to_base'")

    LOGGER.debug(f"Controlling vacuum entity {
                 entity_id} with action: {action}")

    result = await make_service_call_with_action(entity_id, action, "hass_vacuum_control")

    return result


async def hass_media_control(entity_id: str, action: str):
    """Control the media player entity specified in the 'entity_id' parameter with the action specified in the 'action' parameter.

    Args:
        entity_id: A string containing the entity ID of the media player device that needs to be controlled.
        action: The action to perform on the media player (choices: ['media_play', 'media_pause', 'media_stop', 'media_next_track', 'media_previous_track', 'volume_up', 'volume_down', 'volume_mute', 'media_shuffle_set']).

    """

    if action not in [act.value for act in MediaAction]:
        raise ValueError(
            "action must be one of the supported actions: 'media_play', 'media_pause', 'media_stop', 'media_next_track', 'media_previous_track', 'volume_up', 'volume_down', 'volume_mute', 'media_shuffle_set'")

    LOGGER.debug(f"Controlling media player {
                 entity_id} with action: {action.value}")

    result = await make_service_call_with_action(entity_id, action, "hass_media_control")

    return result


async def hass_fan_control(entity_id: str, action: str):
    """Control the fan entity specified in the 'entity_id' parameter with the action specified in the 'action' parameter.

    Args:
        entity_id: A string containing the entity ID of the fan device that needs to be controlled.
        action: The action to perform on the fan (choices: ['increase_speed', 'decrease_speed']).

    """

    if action not in [act.value for act in FanAction]:
        raise ValueError(
            "action must be one of the supported actions: 'increase_speed', 'decrease_speed'")

    LOGGER.debug(f"Controlling fan {entity_id} with action: {action.value}")

    result = await make_service_call_with_action(entity_id, action, "hass_fan_control")

    return result


async def hass_set_temperature(entity_id: str, temperature: float):
    """Set the temperature of the climate entity specified in the 'entity_id' parameter to the value specified in the 'temperature' parameter.

    Only supported for climate devices.

    Args:
        entity_id: Entity ID of the climate entity that needs to have its temperature set.
        temperature: The temperature value to set.

    """

    if not isinstance(temperature, int | float):
        raise TypeError("temperature must be a number")

    if not isinstance(entity_id, str):
        raise TypeError("entity_id must be a string")

    if temperature < 0:
        raise ValueError("temperature must be greater than or equal to 0")

    LOGGER.debug(f"Setting temperature of entity {entity_id} to {temperature}")

    thermostat_attributes = await HomeAssistantService.async_get_thermostat_mode(
        entity_id)

    if thermostat_attributes.hvac_mode == HVACMode.OFF.value:
        LOGGER.debug(
            f"{entity_id} is turned off. Turning it on and setting the temperature.")

        result = await make_service_call([entity_id], "turn_on", "hass_turn_on")

        if not result.success:
            return str(result)
        else:
            thermostat_attributes = await HomeAssistantService.async_get_thermostat_mode(
                entity_id)

    if thermostat_attributes.hvac_mode == HVACMode.AUTO.value or thermostat_attributes.hvac_mode == HVACMode.HEAT_COOL.value:
        LOGGER.debug(
            f"{entity_id} is in auto mode. Setting the target high temperature and retaining the target low temperature.")

        result = await make_service_call_with_data(entity_id, "set_temperature", {
            "target_temp_low": thermostat_attributes.target_temperature_low,
            "target_temp_high": temperature
        }, "hass_set_temperature")

        return result

    if thermostat_attributes.hvac_mode == HVACMode.HEAT.value or thermostat_attributes.hvac_mode == HVACMode.COOL.value:
        LOGGER.debug(
            f"{entity_id} is in heat or cool mode. Setting the temperature.")

        result = await make_service_call_with_data(entity_id, "set_temperature", {
            "temperature": temperature
        }, "hass_set_temperature")

        return result

    return "Something went wrong"


async def hass_set_humidity(entity_id: str, humidity: float):
    """Set the humidity of the entity specified in the 'entity_id' parameter to the value specified in the 'humidity' parameter.

    Only supported for climate devices.

    Args:
        entity_id: Entity ID of the climate entity that needs to have its humidity set.
        humidity: The desired humidity.

    """

    if not isinstance(humidity, int | float):
        raise TypeError("temperature must be a number")

    if not isinstance(entity_id, str):
        raise TypeError("entity_id must be a string")

    LOGGER.debug(f"Setting humidity of entity {entity_id} to {humidity}")

    result = await make_service_call_with_data(entity_id, "set_humidity", {
        "humidity": humidity
    }, "hass_set_humidity")

    return result


async def hass_set_fan_mode(entity_id: str, fan_mode: str):
    """Set the fan mode of the entity specified in the 'entity_id' parameter to the value specified in the 'fan_mode' parameter.

    Only supported for climate devices.

    Args:
        entity_id: Entity ID of the climate entity that needs to have its fan mode set.
        fan_mode: The fan mode to set (choices: ['On Low', 'On High', 'Auto Low', 'Auto High', 'Off']).

    """

    if fan_mode not in [mode.value for mode in FanMode]:
        raise ValueError(
            "fan_mode must be one of the supported fan modes: 'On Low', 'On High', 'Auto Low', 'Auto High', 'Off'")

    LOGGER.debug(f"Setting fan mode of entity {entity_id} to {fan_mode.value}")

    result = await make_service_call_with_data(entity_id, "set_fan_mode", {
        "fan_mode": fan_mode
    }, "hass_set_fan_mode")

    return result


async def hass_set_hvac_mode(entity_id: str, hvac_mode: str):
    """Set the HVAC mode of the entity specified in the 'entity_id' parameter to the value specified in the 'hvac_mode' parameter.

    Only supported for climate devices.

    Args:
        entity_id: Entity ID of the climate entity that needs to have its HVAC mode set.
        hvac_mode: The HVAC mode to set (choices: ['off', 'heat', 'cool', 'auto', 'heat_cool', 'fan_only']).

    """

    if hvac_mode not in [mode.value for mode in HVACMode]:
        raise ValueError(
            "hvac_mode must be one of the supported HVAC modes: 'off', 'heat', 'cool', 'auto', 'heat_cool', 'fan_only'")

    LOGGER.debug(f"Setting HVAC mode of entity {
                 entity_id} to {hvac_mode.value}")

    result = await make_service_call_with_data(entity_id, "set_hvac_mode", {
        "hvac_mode": hvac_mode
    }, "hass_set_hvac_mode")

    return result


async def hass_set_preset_mode(entity_id: str, preset_mode: str):
    """Set the preset mode of the entity specified in the 'entity_id' parameter to the value specified in the 'preset_mode' parameter.

    Only supported for climate devices.

    Args:
        entity_id: Entity ID of the climate entity that needs to have its preset mode set.
        preset_mode: The preset mode to set (choices: ['home', 'away', 'eco', 'auto']).

    """

    if preset_mode not in [mode.value for mode in PresetMode]:
        raise ValueError(
            "preset_mode must be one of the supported preset modes: 'home', 'away', 'eco', 'auto'")

    LOGGER.debug(f"Setting preset mode of entity {
                 entity_id} to {preset_mode.value}")

    result = await make_service_call_with_data(entity_id, "set_preset_mode", {
        "preset_mode": preset_mode
    }, "hass_set_preset_mode")

    return result


async def hass_get_agenda(entity_ids: list[str], start_date: str, end_date: str):
    """Get upcoming events on the calendars specified in the 'entity_ids' parameter between the 'start_date' and 'end_date'.

    Args:
        entity_ids: The entity IDs calendar devices to get events from.
        start_date: The start date for the agenda, specified in the format 'YYYY-MM-DD HH:MM:SS'.
        end_date: The end date for the agenda, specified in the format 'YYYY-MM-DD HH:MM:SS'.

    """

    if not isinstance(entity_ids, list) or not all(isinstance(id, str) for id in entity_ids):
        raise ValueError("entity_ids must be a list of strings")

    if len(entity_ids) < 1:
        raise ValueError("entity_ids must contain at least one entity ID")

    validate_time_range(start_date, end_date)

    LOGGER.debug(f"Getting agenda for calendars: {', '.join(
        entity_ids)} between {start_date} and {end_date}")

    domain_entity_map = {}
    tool_call_result = ToolCallResult()

    validate_entity_ids(entity_ids, domain_entity_map,
                        tool_call_result, "hass_get_agenda")

    result = await HomeAssistantService.async_get_calendar_events(
        entity_ids, start_date, end_date)

    if result.success:
        return result.data
    else:
        return str(result)


async def hass_get_availability(entity_id: str, start_date: str, end_date: str):
    """Find time slots that are open in the calendar with entity_id between the 'start_date' and 'end_date'.

    Args:
        entity_id: The entity IDs calendar devices to get events from.
        start_date: The start date for the agenda, specified in the format 'YYYY-MM-DD HH:MM:SS'.
        end_date: The end date for the agenda, specified in the format 'YYYY-MM-DD HH:MM:SS'.

    """

    if not isinstance(entity_id, str):
        raise TypeError("entity_id must be a string")

    validate_time_range(start_date, end_date)

    LOGGER.debug(f"Getting available time slots for calendar: {
                 entity_id} between {start_date} and {end_date}")

    result = await HomeAssistantService.async_get_calendar_availability(
        entity_id, start_date, end_date)

    if result.success:
        return result.data
    else:
        return str(result)


async def hass_create_event(entity_id: str, start_date: str, end_date: str, summary: str):
    """Create an event in the calendar with entity_id between the 'start_date' and 'end_date'.

    Args:
        entity_id: The entity IDs calendar devices to get events from.
        start_date: The start date for the agenda, specified in the format 'YYYY-MM-DD HH:MM:SS'.
        end_date: The end date for the agenda, specified in the format 'YYYY-MM-DD HH:MM:SS'.
        summary: The summary of the event.

    """

    if not isinstance(entity_id, str):
        raise TypeError("entity_id must be a string")

    validate_time_range(start_date, end_date)

    LOGGER.debug(f"Creating event for calendar: {
                 entity_id} between {start_date} and {end_date}")

    result = await HomeAssistantService.async_create_calendar_event(
        entity_id, start_date, end_date, summary)

    return str(result)


def hass_get_current_user():
    """Get the current user."""
    return "Hemanth Pai"


tools = [
    get_json_schema(hass_turn_on),
    get_json_schema(hass_turn_off),
    get_json_schema(hass_toggle),
    get_json_schema(hass_open),
    get_json_schema(hass_close),
    get_json_schema(hass_set_temperature),
    get_json_schema(hass_set_humidity),
    get_json_schema(hass_set_fan_mode),
    get_json_schema(hass_set_hvac_mode),
    get_json_schema(hass_set_preset_mode),
    get_json_schema(hass_lock),
    get_json_schema(hass_unlock),
    get_json_schema(hass_vacuum_control),
    get_json_schema(hass_fan_control),
    get_json_schema(hass_media_control),
    get_json_schema(hass_get_current_user),
    get_json_schema(hass_get_agenda),
    get_json_schema(hass_get_availability),
    get_json_schema(hass_create_event),
]

TOOL_FUNCTIONS = {
    "hass_turn_on": hass_turn_on,
    "hass_turn_off": hass_turn_off,
    "hass_toggle": hass_toggle,
    "hass_open": hass_open,
    "hass_close": hass_close,
    "hass_set_temperature": hass_set_temperature,
    "hass_set_humidity": hass_set_humidity,
    "hass_set_fan_mode": hass_set_fan_mode,
    "hass_set_hvac_mode": hass_set_hvac_mode,
    "hass_set_preset_mode": hass_set_preset_mode,
    "hass_lock": hass_lock,
    "hass_unlock": hass_unlock,
    "hass_vacuum_control": hass_vacuum_control,
    "hass_fan_control": hass_fan_control,
    "hass_media_control": hass_media_control,
    "hass_get_current_user": hass_get_current_user,
    "hass_get_agenda": hass_get_agenda,
    "hass_get_availability": hass_get_availability,
    "hass_create_event": hass_create_event,
}
