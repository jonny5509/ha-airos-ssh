from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN
import re

BASE_SENSORS = {
    "signal": ("Wireless Signal", "dBm"),
    "noise": ("Wireless Noise", "dBm"),
    "ccq": ("Wireless CCQ", "%"),
    "snr": ("Wireless SNR", "dB"),
    "wlanTxRate": ("Wireless Transmit Rate", "Mbit/s"),
    "wlanRxRate": ("Wireless Receive Rate", "Mbit/s"),
}

OPTIONAL_SENSORS = {
    "essid": ("Wireless Network Name (SSID)", None),
    "frequency": ("Wireless Frequency", "MHz"),
    "wlanMac": ("Wireless MAC Address", None),
    "ethernet_mac": ("Ethernet MAC Address", None),
    "ethernet_interface_state": ("Ethernet Interface State", None),
    "wireless_interface_state": ("Wireless Interface State", None),
    "wireless_mac": ("Wireless MAC Address", None),
    "mac": ("Device MAC Address", None),
    "mode": ("Wireless Mode", None),
    "hostname": ("Hostname", None),
    "uptime_seconds": ("Uptime", "s"),
    "ip_address": ("Device IP Address", None),
    "cpu_model": ("CPU Model", None),
    "cpu_usage": ("CPU Usage", "%"),
    "firmware_upgrade": ("Firmware Upgrade", None),
    "ram_usage_percent": ("RAM Usage", "%"),
    "ethernet_rx_bytes": ("Ethernet Received Data", "B"),
    "ethernet_tx_bytes": ("Ethernet Transmitted Data", "B"),
    "lan_state": ("Ethernet Interface State", None),
    "lan_rxbytes": ("Ethernet Received Data", "B"),
    "lan_rxpackets": ("Ethernet Received Packets", None),
    "lan_rxerrors": ("Ethernet Receive Errors", None),
    "lan_txbytes": ("Ethernet Transmitted Data", "B"),
    "lan_txpackets": ("Ethernet Transmitted Packets", None),
    "lan_txerrors": ("Ethernet Transmit Errors", None),
    "lmac": ("Ethernet MAC Address", None),
    "lip": ("Ethernet IP Address", None),
    "wireless_rx_bytes": ("Wireless Received Data", "B"),
    "wireless_tx_bytes": ("Wireless Transmitted Data", "B"),
}

DEVICE_METADATA = {
    "deviceId": ("Device ID", None),
    "firmwareVersion": ("Firmware Version", None),
    "platform": ("Platform", None),
    "deviceIp": ("Configured Device IP Address", None),
}


def _parse_device_name(raw_name):
    """Split comma-separated AirOS metadata out of the device display name."""
    parts = [part.strip() for part in raw_name.split(",")]
    metadata = {}
    known_keys = {key.lower(): key for key in DEVICE_METADATA}

    # Metadata keys can vary in capitalization between AirOS versions.
    # Match known keys case-insensitively and keep only the clean device name.
    for part in parts[1:]:
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        key = key.strip()
        value = value.strip()
        canonical_key = known_keys.get(key.lower())
        if canonical_key and value:
            metadata[canonical_key] = value

    display_name = parts[0] or "AirOS Device"
    return display_name, metadata


SENSOR_NAME_OVERRIDES = {
    "signal": "Wireless Signal",
    "noise": "Wireless Noise",
    "ccq": "Wireless CCQ",
    "snr": "Wireless SNR",
    "wlanTxRate": "Wireless Transmit Rate",
    "wlanRxRate": "Wireless Receive Rate",
    "wlanMac": "Wireless MAC Address",
    "wireless_mac": "Wireless MAC Address",
    "ethernet_mac": "Ethernet MAC Address",
    "ethernet_interface_state": "Ethernet Interface State",
    "wireless_interface_state": "Wireless Interface State",
    "mac": "Device MAC Address",
    "essid": "Wireless Network Name (SSID)",
    "frequency": "Wireless Frequency",
    "mode": "Wireless Mode",
    "hostname": "Hostname",
    "uptime_seconds": "Uptime",
    "ip_address": "Device IP Address",
    "cpu_model": "CPU Model",
    "cpu_usage": "CPU Usage",
    "firmware_upgrade": "Firmware Upgrade",
    "ram_usage_percent": "RAM Usage",
    "ethernet_rx_bytes": "Ethernet Received Data",
    "ethernet_tx_bytes": "Ethernet Transmitted Data",
    "wireless_rx_bytes": "Wireless Received Data",
    "wireless_tx_bytes": "Wireless Transmitted Data",
    "wip": "Wireless IP Address",
    "wmac": "Wireless MAC Address",
    "apmac": "Access Point MAC Address",
    "channel": "Wireless Channel",
    "date_time": "Radio Date and Time",
    "security": "Wireless Security",
    "qos": "Wireless QoS",
    "antenna": "Antenna Polarization",
    "ack": "ACK Distance",
    "rstatus": "Wireless Radio Status Code",
    "err_nwids": "Wireless Invalid Network IDs",
    "err_crypts": "Wireless Crypto Errors",
    "err_frags": "Wireless Fragment Errors",
    "err_retries": "Wireless Retries",
    "err_beacons": "Wireless Beacon Errors",
    "err_misc": "Wireless Other Errors",
    "lmac": "Ethernet MAC Address",
    "lip": "Ethernet IP Address",
    "lan_state": "Ethernet Interface State",
    "lan_rxbytes": "Ethernet Received Data",
    "lan_rxpackets": "Ethernet Received Packets",
    "lan_rxerrors": "Ethernet Receive Errors",
    "lan_txbytes": "Ethernet Transmitted Data",
    "lan_txpackets": "Ethernet Transmitted Packets",
    "lan_txerrors": "Ethernet Transmit Errors",
    "wlan_rxbytes": "Wireless Received Data",
    "wlan_rxpackets": "Wireless Received Packets",
    "wlan_rxerrors": "Wireless Receive Errors",
    "wlan_txbytes": "Wireless Transmitted Data",
    "wlan_txpackets": "Wireless Transmitted Packets",
    "wlan_txerrors": "Wireless Transmit Errors",
    "ppp_ip": "PPP IP Address",
    "ppp_rxbytes": "PPP Received Data",
    "ppp_rxpackets": "PPP Received Packets",
    "ppp_rxerrors": "PPP Receive Errors",
    "ppp_txbytes": "PPP Transmitted Data",
    "ppp_txpackets": "PPP Transmitted Packets",
    "ppp_txerrors": "PPP Transmit Errors",
    "deviceId": "Device ID",
    "firmwareVersion": "Firmware Version",
    "platform": "Platform",
    "deviceIp": "Configured Device IP Address",
}


def _friendly_name(key):
    """Return a readable, consistently capitalized name for a sensor key."""
    if key in SENSOR_NAME_OVERRIDES:
        return SENSOR_NAME_OVERRIDES[key]

    # Convert camelCase and separators into words before applying protocol terms.
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", key)
    name = re.sub(r"[_-]+", " ", name).strip()
    words = name.split()
    normalized = []
    for word in words:
        lower = word.lower()
        if lower in {"wlan", "wireless", "wifi"}:
            normalized.append("Wireless")
        elif lower in {"lan", "ethernet", "eth"}:
            normalized.append("Ethernet")
        elif lower in {"mac", "ip", "cpu", "ccq", "snr", "ssid", "tx", "rx", "mhz", "dbm", "id", "url", "ram"}:
            normalized.append(lower.upper())
        else:
            normalized.append(lower.capitalize())
    return " ".join(normalized) or "Unknown"


def _device_kind(key):
    """Return the Home Assistant device that should own this sensor."""
    normalized = key.lower()
    # Check WLAN first because "lan" is also present inside "wlan".
    if normalized.startswith(("wlan", "wireless_")) or key in BASE_SENSORS or key in {
        "essid", "frequency", "wireless_mac", "wireless_interface_state", "mode",
    }:
        return "wireless"
    # Keep the single canonical uptime sensor on the main device.
    if key == "uptime_seconds":
        return "main"
    # Legacy AirOS keys may call the wired interface "lan" or "eth".
    if normalized.startswith(("ethernet", "eth")) or re.sub(r"[^a-z0-9]", "", normalized).startswith(("lanstate", "lanrx", "lantx", "lanmac", "lanip")) or key in {"ethernet_mac", "lmac", "lip"}:
        return "ethernet"
    return "main"


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    data = coordinator.data or {}
    display_name, metadata = _parse_device_name(entry.data["name"])
    # Register the parent device first so child devices can reference its ID.
    device_registry = dr.async_get(hass)
    parent_device = device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.data["host"])},
        name=display_name,
        manufacturer="Ubiquiti",
        model=data.get("device_model") or "Ubiquiti AirOS",
    )

    # Ensure the Ethernet child exists, then move existing Ethernet entities
    # back under it. This preserves entity IDs and their history after upgrades.
    host = entry.data["host"]
    ethernet_device = device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, f"{host}_ethernet")},
        name=f"{display_name} Ethernet",
        manufacturer="Ubiquiti",
        model=f"{data.get('device_model') or 'AirOS'} Ethernet",
        via_device=(DOMAIN, host),
    )
    # Always register both interface devices, even when firmware omits optional
    # interface metrics on the first poll.
    wireless_device = device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, f"{host}_wireless")},
        name=f"{display_name} Wireless",
        manufacturer="Ubiquiti",
        model=f"{data.get('device_model') or 'AirOS'} Wireless",
        via_device=(DOMAIN, host),
    )
    entity_registry = er.async_get(hass)

    # Remove registry entries left behind by older releases that exposed raw
    # memory counters as individual sensors. These keys are now attributes on
    # the single RAM Usage sensor, so leaving the old entries creates stale
    # Memory entities in Home Assistant after an upgrade.
    obsolete_memory_keys = {
        "mem_total_bytes",
        "mem_free_bytes",
        "mem_available_bytes",
    }
    host_prefix = f"{host}_"
    for entity in list(entity_registry.entities.values()):
        if entity.config_entry_id != entry.entry_id:
            continue
        if entity.unique_id.startswith(host_prefix):
            old_key = entity.unique_id[len(host_prefix):]
            if old_key in obsolete_memory_keys:
                entity_registry.async_remove(entity.entity_id)

    for entity in entity_registry.entities.values():
        if entity.config_entry_id != entry.entry_id:
            continue
        prefix = f"{host}_"
        if not entity.unique_id.startswith(prefix):
            continue
        key = entity.unique_id[len(prefix):]
        kind = _device_kind(key)
        target_device = (
            ethernet_device if kind == "ethernet"
            else wireless_device if kind == "wireless"
            else None
        )
        if target_device and entity.device_id != target_device.id:
            entity_registry.async_update_entity(
                entity.entity_id, device_id=target_device.id
            )

    # The first probe may not identify the hardware. Update the main device
    # registry entry on later coordinator refreshes once a specific model appears.
    def _update_registered_device_model():
        detected_model = (coordinator.data or {}).get("device_model")
        if detected_model and detected_model != "Ubiquiti AirOS":
            current_device = device_registry.async_get_device(
                identifiers={(DOMAIN, entry.data["host"])}
            )
            if current_device and current_device.model != detected_model:
                device_registry.async_update_device(
                    current_device.id, model=detected_model
                )

    entry.async_on_unload(coordinator.async_add_listener(_update_registered_device_model))

    sensors = [
        AiRXS2Sensor(
            coordinator, entry, key, unit, label, display_name=display_name,
            device_kind=_device_kind(key), parent_device_id=parent_device.id,
        )
        for key, (label, unit) in BASE_SENSORS.items()
    ]

    added_keys = set(BASE_SENSORS)
    for key, (label, unit) in OPTIONAL_SENSORS.items():
        # Prefer the MAC reported directly by AirOS over interface-probe aliases.
        if key == "wireless_mac" and data.get("wlanMac") not in (None, ""):
            added_keys.add(key)
            continue
        # lmac and ethernet_mac can be two names for the same wired interface.
        if key == "lmac" and data.get("ethernet_mac") not in (None, ""):
            added_keys.add(key)
            continue
        # IP discovery depends on an optional SSH probe. Register the entity
        # even if the first probe fails, so it can become available on later polls.
        if key in {"ip_address", "uptime_seconds", "ethernet_interface_state", "wireless_interface_state", "cpu_usage", "firmware_upgrade", "ram_usage_percent"} or data.get(key) not in (None, ""):
            sensors.append(
                AiRXS2Sensor(
                    coordinator, entry, key, unit, label,
                    display_name=display_name, device_kind=_device_kind(key),
                    parent_device_id=parent_device.id,
                )
            )
            added_keys.add(key)

    # Firmware detail fields are attributes of the single Firmware Upgrade sensor,
    # not separate entities of their own.
    added_keys.update(key for key in data if key.startswith("firmware_upgrade_"))
    # Raw memory counters are attributes of RAM Usage, not separate entities.
    added_keys.update({"mem_total_bytes", "mem_free_bytes", "mem_available_bytes"})

    for key, value in data.items():
        # Collapse legacy spellings so one interface has one MAC sensor.
        if key in {"wmac", "wlan_mac", "wireless_mac"} and data.get("wlanMac") not in (None, ""):
            continue
        if key == "lmac" and data.get("ethernet_mac") not in (None, ""):
            continue
        if key not in added_keys and value not in (None, ""):
            sensors.append(
                AiRXS2Sensor(
                    coordinator, entry, key, None, _friendly_name(key),
                    display_name=display_name, device_kind=_device_kind(key),
                    parent_device_id=parent_device.id,
                )
            )

    for key, value in metadata.items():
        label, unit = DEVICE_METADATA[key]
        sensors.append(
            AiRXS2Sensor(
                coordinator, entry, f"device_metadata_{key}", unit, label,
                display_name=display_name, static_value=value, device_kind="main",
                parent_device_id=parent_device.id,
            )
        )

    async_add_entities(sensors)


class AiRXS2Sensor(SensorEntity):
    def __init__(
        self, coordinator, entry, key, unit, label=None, display_name=None,
        static_value=None, device_kind="main", unique_id_suffix=None,
        parent_device_id=None,
    ):
        self.coordinator = coordinator
        self.key = key
        self._entry = entry
        self._display_name = display_name or entry.data["name"]
        self._static_value = static_value
        self._device_kind = device_kind
        self._parent_device_id = parent_device_id
        if device_kind == "ethernet":
            self._device_name = f"{self._display_name} Ethernet"
        elif device_kind == "wireless":
            self._device_name = f"{self._display_name} Wireless"
        else:
            self._device_name = self._display_name
        self._attr_name = f"{self._display_name} {label or key}"
        self._attr_unique_id = f"{entry.data['host']}_{key}" + (
            f"_{unique_id_suffix}" if unique_id_suffix else ""
        )
        if unit:
            self._attr_native_unit_of_measurement = unit

        # Tell Home Assistant how to interpret readings and long-term statistics.
        if key in {"signal", "noise"}:
            self._attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
        elif key == "frequency":
            self._attr_device_class = SensorDeviceClass.FREQUENCY
        elif key == "uptime_seconds":
            self._attr_device_class = SensorDeviceClass.DURATION
        elif key in {"ethernet_rx_bytes", "ethernet_tx_bytes", "lan_rxbytes", "lan_txbytes",
                     "wireless_rx_bytes", "wireless_tx_bytes"}:
            self._attr_device_class = SensorDeviceClass.DATA_SIZE

        if key in {"ethernet_rx_bytes", "ethernet_tx_bytes", "lan_rxbytes", "lan_txbytes",
                   "wireless_rx_bytes", "wireless_tx_bytes"}:
            self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        elif key in {"signal", "noise", "ccq", "snr", "wlanTxRate", "wlanRxRate",
                     "frequency", "cpu_usage",
                     "ram_usage_percent"}:
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def device_info(self):
        host = self._entry.data["host"]
        info = {
            "identifiers": {(DOMAIN, host if self._device_kind == "main" else f"{host}_{self._device_kind}")},
            "name": self._device_name,
            "manufacturer": "Ubiquiti",
            "model": (self.coordinator.data or {}).get("device_model") or "Ubiquiti AirOS" if self._device_kind == "main" else (
                f"{(self.coordinator.data or {}).get('device_model') or 'AirOS'} Ethernet" if self._device_kind == "ethernet" else
                f"{(self.coordinator.data or {}).get('device_model') or 'AirOS'} Wireless"
            ),
        }
        if self._device_kind != "main":
            info["via_device_id"] = self._parent_device_id
        return DeviceInfo(**info)

    @property
    def native_value(self):
        if self._static_value is not None:
            return self._static_value
        return (self.coordinator.data or {}).get(self.key)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        if self.key == "ram_usage_percent":
            return {
                key: data[key]
                for key in ("mem_total_bytes", "mem_free_bytes", "mem_available_bytes")
                if data.get(key) is not None
            }
        if self.key != "firmware_upgrade":
            return None
        return {
            key.removeprefix("firmware_upgrade_"): data[key]
            for key in (
                "firmware_upgrade_installed_version",
                "firmware_upgrade_latest_version",
                "firmware_upgrade_reason",
                "firmware_upgrade_source",
            )
            if data.get(key) is not None
        }
