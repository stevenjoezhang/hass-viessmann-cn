"""The Viessmann CN integration."""

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .client import ViessmannClient, AuthError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["climate", "water_heater", "sensor"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Viessmann CN component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Viessmann CN from a config entry."""
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]

    client = ViessmannClient(username, password)

    try:
        await client.login()
        # Ensure we can get device info
        await client.get_family_devices()
    except AuthError as e:
        _LOGGER.error(f"Authentication failed: {e}")
        return False
    except Exception as e:
        _LOGGER.error(f"Failed to connect: {e}")
        raise ConfigEntryNotReady from e

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = client

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        client = hass.data[DOMAIN].pop(entry.entry_id)
        await client.close()

    return unload_ok
