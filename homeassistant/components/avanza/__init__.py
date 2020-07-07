"""The Avanza integration."""
import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ID
from homeassistant.core import HomeAssistant

from .const import DOMAIN

PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Avanza component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Avanza from a config entry."""
    hass.data[DOMAIN][entry.entry_id] = {
        CONF_ID: entry.data[CONF_ID],
        "type": entry.data["type"],
    }

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
