"""Define tools for interacting with Home Assistant.

This module includes definitions for various tools used in the project, such as functions to interact with Home Assistant entities.

Tools:
    - hass_turn_on: Turn on the entities specified in the 'entity_ids' parameter.
"""

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
