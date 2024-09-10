"""This module provides a HassContextFactory class for singleton access to a HomeAssistant instance."""

from homeassistant.core import HomeAssistant

from .const import LOGGER


class HassContextFactory:
    """Factory class for obtaining a HassContext object."""

    _instance = None

    @classmethod
    def get_instance(cls) -> HomeAssistant:
        """Get an instance of the HassContext object."""
        if cls._instance is None:
            raise ValueError(
                "HassContextFactory hasn't been initialized with a HomeAssistant instance yet.")
        else:
            return cls._instance

    @classmethod
    def set_instance(cls, hass: HomeAssistant) -> None:
        """Set the HomeAssistant instance for the factory."""
        if cls._instance is not None:
            LOGGER.warning(
                "HassContextFactory already has a HomeAssistant instance set. Ignoring.")
        elif not isinstance(hass, HomeAssistant):
            raise ValueError(
                "HassContextFactory.set_instance() requires a HomeAssistant instance.")
        else:
            cls._instance = hass
