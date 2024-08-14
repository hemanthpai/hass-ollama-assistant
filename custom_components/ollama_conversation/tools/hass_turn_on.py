from typing import List

from ..const import LOGGER

from homeassistant.core import HomeAssistant
from homeassistant.const import ATTR_ENTITY_ID


async def hass_turn_on(hass: HomeAssistant, entity_ids: List[str]):
    """
    Turns on the specified entities.
    Args:
        entity_ids: A list containing of one or more entity IDs of devices or entities that need to be turned on.
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
