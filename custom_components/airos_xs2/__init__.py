"""Set up the Ubiquiti AirOS SSH integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, Platform

from .const import DOMAIN
from .coordinator import AiRXS2Coordinator

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up an AirOS device."""
    coordinator = AiRXS2Coordinator(
        hass,
        entry.data["host"],
        entry.data["username"],
        entry.data["password"],
        entry.data["name"],
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload an AirOS device."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        if not hass.data.get(DOMAIN):
            hass.data.pop(DOMAIN, None)
    return unloaded
