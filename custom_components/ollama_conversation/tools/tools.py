from .hass_turn_on import hass_turn_on
from ..utils.utils import get_json_schema

tools = [
    {
        "type": "function",
        "function": {
            "name": "hass_turn_on",
            "description": "Turn on the entities specified in the 'entity_ids' parameter",
            "parameters": {
                "type": "object",
                "properties": {
                    "entity_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1,
                        "description": "A list containing of one or more entity IDs of devices or entities that need to be turned on.",
                    }
                },
                "required": ["entity_ids"],
            },
        },
    }
]
