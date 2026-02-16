"""Water heater platform for Viessmann CN."""

import logging
from typing import Any, List, Optional

from homeassistant.components.water_heater import (
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.const import UnitOfTemperature, ATTR_TEMPERATURE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .client import ViessmannClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Viessmann water heater device."""
    client = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ViessmannWaterHeater(client)], True)


class ViessmannWaterHeater(WaterHeaterEntity):
    """Representation of a Viessmann Water Heater device."""

    def __init__(self, client: ViessmannClient):
        """Initialize the water heater device."""
        self._client = client
        self._attr_name = "Viessmann Hot Water"
        self._attr_unique_id = f"{client._username}_dhw"
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_supported_features = WaterHeaterEntityFeature.TARGET_TEMPERATURE
        self._attr_target_temperature_step = 1.0
        self._attr_min_temp = 30
        self._attr_max_temp = 60
        self._status = {}
        self._scan_status = {}

    async def async_update(self) -> None:
        """Get the latest data from the device."""
        try:
            self._status = await self._client.update()
            self._scan_status = await self._client.get_scan_status()

            # Update attributes
            req_data = self._status.get("boilerRequestData", {})

            # Target temperature
            self._attr_target_temperature = req_data.get("dhwSet")

            # Current temperature (using dhwProbe from scan status)
            self._attr_current_temperature = self._scan_status.get("dhwProbe")

            # Min/Max temp
            if req_data.get("dhwMinSet"):
                self._attr_min_temp = float(req_data.get("dhwMinSet"))
            if req_data.get("dhwMaxSet"):
                self._attr_max_temp = float(req_data.get("dhwMaxSet"))

            # Operation mode (always on for DHW usually, or based on main mode)
            # We can just say "gas" or "eco" etc, but for now let's keep it simple
            self._attr_current_operation = (
                "heating" if self._scan_status.get("fire") == 1 else "idle"
            )

        except Exception as e:
            _LOGGER.error(f"Error updating water heater entity: {e}")

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temp := kwargs.get(ATTR_TEMPERATURE)) is None:
            return

        await self._client.set_dhw_temp(temp)
        # Force update to reflect changes immediately
        await self.async_update()
        self.async_write_ha_state()

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Set operation mode."""
        # Not really applicable for just DHW part usually, unless we want to turn off DHW completely
        # which might be done via main mode. For now, pass.
        pass
