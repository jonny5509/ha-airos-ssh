"""Set up the Ubiquiti AirOS SSH integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.importlib import async_import_module

from .const import DOMAIN

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up an AirOS device."""
    # asyncssh and the coordinator's parsing dependencies are relatively heavy.
    # Import them through Home Assistant's import executor to avoid blocking the
    # event loop when the integration is first loaded.
    coordinator_module = await async_import_module(
        hass, f"{__package__}.coordinator"
    )
    coordinator = coordinator_module.AiRXS2Coordinator(
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
