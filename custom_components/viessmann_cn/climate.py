"""Climate platform for Viessmann CN."""

import logging
from typing import Any, List, Optional

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVACMode,
    ClimateEntityFeature,
)
from homeassistant.const import UnitOfTemperature, ATTR_TEMPERATURE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .client import ViessmannClient

_LOGGER = logging.getLogger(__name__)

# Mapping Viessmann modes to HA HVAC modes
# 10: Standby/Off
# 15: DHW only (Heating Off)
# 20: Heating + DHW
MODE_TO_HVAC = {
    10: HVACMode.OFF,
    15: HVACMode.OFF,  # Treated as heating off
    20: HVACMode.HEAT,
}

HVAC_TO_MODE = {
    HVACMode.OFF: 15,  # Default to DHW only when turning heating off
    HVACMode.HEAT: 20,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Viessmann climate device."""
    client = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ViessmannClimate(client)], True)


class ViessmannClimate(ClimateEntity):
    """Representation of a Viessmann Climate device."""

    def __init__(self, client: ViessmannClient):
        """Initialize the climate device."""
        self._client = client
        self._attr_name = "Viessmann Heating"
        self._attr_unique_id = f"{client._username}_heating"
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
        self._attr_target_temperature_step = 1.0
        self._attr_min_temp = 30
        self._attr_max_temp = 80
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
            self._attr_target_temperature = req_data.get("chSet")

            # Current temperature (using chProbe from scan status)
            self._attr_current_temperature = self._scan_status.get("chProbe")

            # Min/Max temp
            if req_data.get("chMin"):
                self._attr_min_temp = float(req_data.get("chMin"))
            if req_data.get("chMax"):
                self._attr_max_temp = float(req_data.get("chMax"))

            # HVAC Mode
            mode = req_data.get("mode")
            self._attr_hvac_mode = MODE_TO_HVAC.get(mode, HVACMode.OFF)

            # HVAC Action (Heating or Idle)
            # fire: 1 means burning
            is_burning = self._scan_status.get("fire") == 1
            if self._attr_hvac_mode == HVACMode.HEAT and is_burning:
                self._attr_hvac_action = "heating"
            else:
                self._attr_hvac_action = "idle"

        except Exception as e:
            _LOGGER.error(f"Error updating climate entity: {e}")

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        if hvac_mode not in HVAC_TO_MODE:
            _LOGGER.warning(f"Unsupported mode: {hvac_mode}")
            return

        viessmann_mode = HVAC_TO_MODE[hvac_mode]
        await self._client.set_mode(viessmann_mode)
        # Force update to reflect changes immediately
        await self.async_update()
        self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temp := kwargs.get(ATTR_TEMPERATURE)) is None:
            return

        await self._client.set_heating_temp(temp)
        # Force update to reflect changes immediately
        await self.async_update()
        self.async_write_ha_state()
