"""Maintenance controls for legacy airOS devices over SSH."""
import asyncssh
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, device_identifier


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    # Remove the legacy reboot switch registry entry after migrating to a button.
    entity_registry = er.async_get(hass)
    legacy_unique_ids = {f"{entry.data['host']}_reboot", f"{device_identifier(entry.data['host'])}_reboot"}
    for entity in list(entity_registry.entities.values()):
        if (entity.config_entry_id == entry.entry_id and entity.domain == "switch"
                and entity.unique_id in legacy_unique_ids):
            entity_registry.async_remove(entity.entity_id)
    async_add_entities([AirOSRebootButton(coordinator, entry)])


class AirOSRebootButton(ButtonEntity):
    """Reboot the airOS device without factory-resetting it."""

    _attr_has_entity_name = True
    _attr_name = "Reboot"
    _attr_icon = "mdi:restart"

    def __init__(self, coordinator, entry):
        super().__init__()
        self._coordinator = coordinator
        self._attr_unique_id = f"{device_identifier(entry.data['host'])}_reboot"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_identifier(entry.data["host"]))},
            manufacturer="Ubiquiti",
            model=(coordinator.data or {}).get("device_model") or "Original airOS 3.x–4.x",
            name=entry.data["name"].split(",", 1)[0].strip() or "AirOS Device",
        )

    async def async_press(self):
        """Request a normal reboot over SSH."""
        async with asyncssh.connect(
            self._coordinator.host,
            username=self._coordinator.username,
            password=self._coordinator.password,
            known_hosts=None,
            kex_algs=["diffie-hellman-group1-sha1"],
            encryption_algs=["aes128-cbc"],
            server_host_key_algs=["ssh-rsa"],
        ) as conn:
            await conn.run("reboot")
