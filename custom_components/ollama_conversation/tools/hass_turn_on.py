"""This module provides a function to turn on specified entities in Home Assistant.

Functions:
    hass_turn_on(hass: HomeAssistant, entity_ids: list[str]) -> str:
        Turns on the specified entities.

    hass_turn_off(hass: HomeAssistant, entity_ids: list[str]) -> str:
        Turns off the specified entities.
"""
from ..const import LOGGER

from homeassistant.core import HomeAssistant
from homeassistant.const import ATTR_ENTITY_ID


async def hass_turn_on(hass: HomeAssistant, entity_ids: list[str]):
    """Turn on specified entities in Home Assistant.

    Args:
        entity_ids: A list containing of one or more entity IDs of devices or entities that need to be turned on.
        hass: The Home Assistant instance.

    """
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


async def hass_turn_off(hass: HomeAssistant, entity_ids: list[str]):
    """Turn off specified entities in Home Assistant.

    Args:
        entity_ids: A list containing of one or more entity IDs of devices or entities that need to be turned off.
        hass: The Home Assistant instance.

    """
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
