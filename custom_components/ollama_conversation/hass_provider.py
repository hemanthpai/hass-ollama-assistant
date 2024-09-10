"""This module provides a HassContext class for singleton access to a HomeAssistant instance."""

from homeassistant.core import HomeAssistant


class HassContext:
    """Singleton access to an instance of the HomeAssistant object."""

    _instance = None

    def __init__(self, hass: HomeAssistant):
        """Initialize the HassContext object."""
        self.hass = hass

    def __new__(cls, *args, **kwargs):
        """Create a new instance of the class."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
