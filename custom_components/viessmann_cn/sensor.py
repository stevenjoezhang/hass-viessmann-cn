"""Sensor platform for Viessmann CN."""

import logging
from typing import Any, List, Optional

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature, PERCENTAGE
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
    """Set up the Viessmann sensor device."""
    client = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ViessmannSensor(client)], True)


class ViessmannSensor(SensorEntity):
    """Representation of a Viessmann Sensor device."""

    def __init__(self, client: ViessmannClient):
        """Initialize the sensor device."""
        self._client = client
        self._attr_name = "Viessmann Status"
        self._attr_unique_id = f"{client._username}_status"
        self._attr_device_class = SensorDeviceClass.ENUM
        self._status = {}
        self._scan_status = {}

    async def async_update(self) -> None:
        """Get the latest data from the device."""
        try:
            self._status = await self._client.update()
            self._scan_status = await self._client.get_scan_status()

            # Update attributes
            # Fault status
            fault = self._status.get("faultStatus")
            if fault:
                self._attr_native_value = f"Fault: {fault}"
            else:
                self._attr_native_value = "Normal"

            # Additional attributes
            self._attr_extra_state_attributes = {
                "fire": self._scan_status.get("fire"),
                "running_status": self._scan_status.get("runningStatus"),
                "sys_pattern": self._scan_status.get("sysPattern"),
                "mode_name": self._scan_status.get("modeName"),
                "wifi_firmware": self._scan_status.get("wifiFirmwareVersion"),
                "ch_probe": self._scan_status.get("chProbe"),
                "dhw_probe": self._scan_status.get("dhwProbe"),
            }

        except Exception as e:
            _LOGGER.error(f"Error updating sensor entity: {e}")
