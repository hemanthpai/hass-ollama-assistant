"""This module provides tools for interacting with Home Assistant entities."""

from enum import Enum
from homeassistant.const import ATTR_ENTITY_ID

from .json_schema import get_json_schema

from .const import LOGGER

from .hass_provider import HassContextFactory


class MediaAction(Enum):
    """An enumeration representing the actions that can be performed on a media player."""

    PLAY = "play"
    PAUSE = "pause"
    STOP = "stop"
    NEXT = "next"
    PREVIOUS = "previous"
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"
    VOLUME_MUTE = "volume_mute"


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


async def hass_turn_on(entity_ids: list[str]):
    """Turn on the entities specified in the 'entity_ids' parameter.

    Supported entity types are: light, switch, fan, climate, media_player, automation, script, scene, and vacuum.

    Args:
        entity_ids: The entity IDs of devices or entities that need to be turned on.

    """
    if not isinstance(entity_ids, list) or not all(isinstance(id, str) for id in entity_ids):
        raise ValueError("entity_ids must be a list of strings")
    if len(entity_ids) < 1:
        raise ValueError("entity_ids must contain at least one entity ID")

    LOGGER.debug(f"Turning on entities: {', '.join(entity_ids)}")

    hass = HassContextFactory.get_instance()
    for entity_id in entity_ids:
        domain = entity_id.split(".")[0]
        # TODO: Add error handling for making sure a valid domain exists for the entity_id
        try:
            await hass.services.async_call(
                domain,
                "turn_on",
                {ATTR_ENTITY_ID: entity_id},
                blocking=True,
            )
        except Exception as e:
            LOGGER.error(f"Error while turning on entity {entity_id}: {e}")
            return f"Error while turning on entity {entity_id}"

    return "Turned on the specified entities."


async def hass_turn_off(entity_ids: list[str]):
    """Turn off the entities specified in the 'entity_ids' parameter.

    Supported entity types are: light, switch, fan, climate, media_player, automation, script, and vacuum.

    Args:
        entity_ids: The entity IDs of devices or entities that need to be turned off.

    """
    if not isinstance(entity_ids, list) or not all(isinstance(id, str) for id in entity_ids):
        raise ValueError("entity_ids must be a list of strings")
    if len(entity_ids) < 1:
        raise ValueError("entity_ids must contain at least one entity ID")

    LOGGER.debug(f"Turning off entities: {', '.join(entity_ids)}")

    hass = HassContextFactory.get_instance()
    for entity_id in entity_ids:
        domain = entity_id.split(".")[0]

        try:
            await hass.services.async_call(
                domain,
                "turn_off",
                {ATTR_ENTITY_ID: entity_id},
                blocking=True,
            )
        except Exception as e:
            LOGGER.error(f"Error while turning off entity {entity_id}: {e}")
            return f"Error while turning off entity {entity_id}"

    return "Turned off the specified entities."


def hass_toggle(entity_ids: list[str]):
    """Toggle the entities specified in the 'entity_ids' parameter.

    Supported entity types are: light, switch, fan, climate, media_player, lock, cover, automation, script, and vacuum.

    Args:
        entity_ids: The entity IDs of devices or entities that need to be toggled.

    """
    if not isinstance(entity_ids, list) or not all(isinstance(id, str) for id in entity_ids):
        raise ValueError("entity_ids must be a list of strings")
    if len(entity_ids) < 1:
        raise ValueError("entity_ids must contain at least one entity ID")

    LOGGER.debug(f"Toggling entities: {', '.join(entity_ids)}")


def hass_open(entity_ids: list[str]):
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


def hass_close(entity_ids: list[str]):
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


def hass_set_temperature(entity_id: str, temperature: float):
    """Set the temperature of the climate entity specified in the 'entity_id' parameter to the value specified in the 'temperature' parameter.

    Only supported for climate devices.

    Args:
        entity_id: Entity ID of the climate entity that needs to have its temperature set.
        temperature: The temperature value to set.

    """

    LOGGER.debug(f"Setting temperature of entity {entity_id} to {temperature}")


def hass_set_humidity(entity_id: str, humidity: float):
    """Set the humidity of the entity specified in the 'entity_id' parameter to the value specified in the 'humidity' parameter.

    Only supported for climate devices.

    Args:
        entity_id: Entity ID of the climate entity that needs to have its humidity set.
        humidity: The desired humidity.

    """

    LOGGER.debug(f"Setting humidity of entity {entity_id} to {humidity}")


def hass_set_fan_mode(entity_id: str, fan_mode: str):
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


def hass_set_hvac_mode(entity_id: str, hvac_mode: str):
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


def hass_set_preset_mode(entity_id: str, preset_mode: str):
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


def hass_lock(entity_ids: list[str]):
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


def hass_unlock(entity_ids: list[str]):
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


def hass_vacuum_start(entity_ids: list[str]):
    """Start the vacuum entities specified in the 'entity_ids' parameter.

    Args:
        entity_ids: The entity IDs of vacuum devices that need to be started.

    """

    if not isinstance(entity_ids, list) or not all(isinstance(id, str) for id in entity_ids):
        raise ValueError("entity_ids must be a list of strings")
    if len(entity_ids) < 1:
        raise ValueError("entity_ids must contain at least one entity ID")

    LOGGER.debug(f"Starting vacuum entities: {', '.join(entity_ids)}")


def hass_vacuum_stop(entity_ids: list[str]):
    """Stop the vacuum entities specified in the 'entity_ids' parameter.

    Args:
        entity_ids: The entity IDs of vacuum devices that need to be stopped.

    """

    if not isinstance(entity_ids, list) or not all(isinstance(id, str) for id in entity_ids):
        raise ValueError("entity_ids must be a list of strings")
    if len(entity_ids) < 1:
        raise ValueError("entity_ids must contain at least one entity ID")

    LOGGER.debug(f"Stopping vacuum entities: {', '.join(entity_ids)}")


def hass_vacuum_pause(entity_ids: list[str]):
    """Pause the vacuum entities specified in the 'entity_ids' parameter.

    Args:
        entity_ids: The entity IDs of vacuum devices that need to be paused.

    """

    if not isinstance(entity_ids, list) or not all(isinstance(id, str) for id in entity_ids):
        raise ValueError("entity_ids must be a list of strings")
    if len(entity_ids) < 1:
        raise ValueError("entity_ids must contain at least one entity ID")

    LOGGER.debug(f"Pausing vacuum entities: {', '.join(entity_ids)}")


def hass_return_to_base(entity_ids: list[str]):
    """Return the vacuum entities specified in the 'entity_ids' parameter to their base station.

    Args:
        entity_ids: The entity IDs of vacuum devices that need to return to their base station.

    """

    if not isinstance(entity_ids, list) or not all(isinstance(id, str) for id in entity_ids):
        raise ValueError("entity_ids must be a list of strings")
    if len(entity_ids) < 1:
        raise ValueError("entity_ids must contain at least one entity ID")

    LOGGER.debug(f"Returning vacuum entities to base station: {
                 ', '.join(entity_ids)}")


def hass_increase_speed(entity_ids: list[str]):
    """Increase the speed of the fan entities specified in the 'entity_ids' parameter.

    Args:
        entity_ids: The entity IDs of fan devices that need to have their speed increased.

    """

    if not isinstance(entity_ids, list) or not all(isinstance(id, str) for id in entity_ids):
        raise ValueError("entity_ids must be a list of strings")
    if len(entity_ids) < 1:
        raise ValueError("entity_ids must contain at least one entity ID")

    LOGGER.debug(f"Increasing speed of fan entities: {', '.join(entity_ids)}")


def hass_decrease_speed(entity_ids: list[str]):
    """Decrease the speed of the fan entities specified in the 'entity_ids' parameter.

    Args:
        entity_ids: The entity IDs of fan devices that need to have their speed decreased.

    """

    if not isinstance(entity_ids, list) or not all(isinstance(id, str) for id in entity_ids):
        raise ValueError("entity_ids must be a list of strings")
    if len(entity_ids) < 1:
        raise ValueError("entity_ids must contain at least one entity ID")

    LOGGER.debug(f"Decreasing speed of fan entities: {', '.join(entity_ids)}")


def hass_media_control(entity_id: str, action: str):
    """Control the media player entity specified in the 'entity_id' parameter with the action specified in the 'action' parameter.

    Args:
        entity_id: A string containing the entity ID of the media player device that needs to be controlled.
        action: The action to perform on the media player (choices: ['play', 'pause', 'stop', 'next', 'previous', 'volume_up', 'volume_down', 'volume_mute']).

    """

    if action not in [act.value for act in MediaAction]:
        raise ValueError(
            "action must be one of the supported actions: 'play', 'pause', 'stop', 'next', 'previous', 'volume_up', 'volume_down', 'volume_mute'")

    LOGGER.debug(f"Controlling media player {
                 entity_id} with action: {action.value}")


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
    get_json_schema(hass_vacuum_start),
    get_json_schema(hass_vacuum_stop),
    get_json_schema(hass_vacuum_pause),
    get_json_schema(hass_return_to_base),
    get_json_schema(hass_increase_speed),
    get_json_schema(hass_decrease_speed),
    get_json_schema(hass_media_control),
    get_json_schema(hass_get_current_user),
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
    "hass_vacuum_start": hass_vacuum_start,
    "hass_vacuum_stop": hass_vacuum_stop,
    "hass_vacuum_pause": hass_vacuum_pause,
    "hass_return_to_base": hass_return_to_base,
    "hass_increase_speed": hass_increase_speed,
    "hass_decrease_speed": hass_decrease_speed,
    "hass_media_control": hass_media_control,
    "hass_get_current_user": hass_get_current_user,
}
