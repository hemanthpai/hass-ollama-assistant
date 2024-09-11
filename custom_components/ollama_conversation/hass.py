"""This module provides a service class for interacting with Home Assistant."""

from .hass_provider import HassContextFactory

from .const import LOGGER

from homeassistant.const import ATTR_ENTITY_ID


class HomeAssistantServiceResult:
    """Result of a service call."""

    def __init__(self, success: bool, error: list[str] | None = None):
        """Initialize the result."""
        self.success = success
        self.error = error

    def __str__(self):
        """Return a string representation of the result."""
        return f"Success: {self.success}, Error: {self.error}"


class HomeAssistantService:
    """Service class for interacting with Home Assistant."""

    @staticmethod
    async def async_call_service(entity_ids: list[str], domain: str, service: str, data: dict = None) -> HomeAssistantServiceResult:
        """Call a service."""

        hass = HassContextFactory.get_instance()

        service_data = {ATTR_ENTITY_ID: entity_ids}
        if data is not None:
            service_data.update(data)

        try:
            await hass.services.async_call(
                domain,
                service,
                service_data,
                blocking=True,
            )

            return HomeAssistantServiceResult(success=True)
        except Exception as e:
            LOGGER.error(f"Error while turning on entities {entity_ids}: {e}")
            return HomeAssistantServiceResult(success=False, error=[entity_ids])
