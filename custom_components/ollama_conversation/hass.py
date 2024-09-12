"""This module provides a service class for interacting with Home Assistant."""

import json
from .hass_provider import HassContextFactory

from .const import LOGGER

from .helpers import generate_available_time_slots_from_calendar_events

from homeassistant.const import ATTR_ENTITY_ID


class ThermostatAttributes:
    """Attributes of a thermostat."""

    def __init__(self, hvac_mode: str, target_temperature_low: float | None, target_temperature_high: float | None):
        """Initialize the attributes."""
        self.hvac_mode = hvac_mode
        self.target_temperature_low = target_temperature_low
        self.target_temperature_high = target_temperature_high

    def __str__(self):
        """Return a string representation of the attributes."""
        return f"Mode: {self.hvac_mode}, Low: {self.target_temperature_low}, High: {self.target_temperature_high}"


class HomeAssistantServiceResult:
    """Result of a service call."""

    def __init__(self, success: bool, error: list[str] | None = None, data=None):
        """Initialize the result."""
        self.success = success
        self.error = error
        self.data = data

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

    @staticmethod
    async def async_get_thermostat_mode(entity_id: str) -> ThermostatAttributes:
        """Get the current thermostat mode."""
        hass = HassContextFactory.get_instance()
        state = hass.states.get(entity_id)
        target_temperature_low = state.attributes.get("target_temp_low")
        target_temperature_high = state.attributes.get("target_temp_high")
        hvac_mode = state.state

        LOGGER.debug(f"Mode: {hvac_mode}, Low: {
                     target_temperature_low}, High: {target_temperature_high}")

        return ThermostatAttributes(hvac_mode, target_temperature_low, target_temperature_high)

    @staticmethod
    async def async_get_calendar_events(entity_ids: list[str], start_date: str, end_date: str) -> HomeAssistantServiceResult:
        """Get events from a calendar."""
        hass = HassContextFactory.get_instance()

        service_data = {ATTR_ENTITY_ID: entity_ids}
        data = {
            "start_date_time": start_date,
            "end_date_time": end_date
        }
        service_data.update(data)

        try:
            events = await hass.services.async_call(
                "calendar",
                "get_events",
                service_data,
                blocking=True,
                return_response=True
            )

            LOGGER.debug(f"Events: {events}")

            return HomeAssistantServiceResult(success=True, data=json.dumps(events))
        except Exception as e:
            LOGGER.error(f"Error while getting events for calendar {
                entity_ids}: {e}")
            return HomeAssistantServiceResult(success=False, error=[entity_ids])

    @staticmethod
    async def async_get_calendar_availability(entity_id: str, start_date: str, end_date: str) -> HomeAssistantServiceResult:
        """Get availability from a calendar."""
        hass = HassContextFactory.get_instance()

        service_data = {ATTR_ENTITY_ID: entity_id}
        data = {
            "start_date_time": start_date,
            "end_date_time": end_date
        }
        service_data.update(data)

        try:
            events = await hass.services.async_call(
                "calendar",
                "get_events",
                service_data,
                blocking=True,
                return_response=True
            )

            LOGGER.debug(f"Events: {events}")

            list_of_events = events.get(entity_id).get("events")

            available_slots = generate_available_time_slots_from_calendar_events(
                list_of_events, start_date, end_date)

            return HomeAssistantServiceResult(success=True, data=json.dumps(available_slots))

        except Exception as e:
            LOGGER.error(f"Error while getting events for calendar {
                entity_id}: {e}")
            return HomeAssistantServiceResult(success=False, error=[entity_id])

    @staticmethod
    async def async_create_calendar_event(entity_id: str, start_date: str, end_date: str, summary: str) -> HomeAssistantServiceResult:
        """Create a calendar event."""
        hass = HassContextFactory.get_instance()

        service_data = {ATTR_ENTITY_ID: entity_id}

        data = {
            "start_date_time": start_date,
            "end_date_time": end_date,
            "summary": summary
        }

        service_data.update(data)

        try:
            await hass.services.async_call(
                "calendar",
                "create_event",
                service_data,
                blocking=True
            )

            return HomeAssistantServiceResult(success=True)

        except Exception as e:
            LOGGER.error(f"Error while creating event for calendar {
                entity_id}: {e}")
            return HomeAssistantServiceResult(success=False, error=[entity_id])
