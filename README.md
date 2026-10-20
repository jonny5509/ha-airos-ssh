# Ubiquiti AirOS (SSH)

[![Downloads](https://img.shields.io/github/downloads/jonny5509/ha-airos-ssh/total?label=downloads)](https://github.com/jonny5509/ha-airos-ssh/releases)

**Current integration version:** `2.1.7` (see `custom_components/airos_xs2/manifest.json`)

Home Assistant custom integration for legacy Ubiquiti AirOS devices (NanoStation2, NanoStation5, PowerStation2, and related hardware). This variant connects over SSH and runs read-only status commands on the radio.

## What's new in v2.1.7

The integration manifest currently declares version `2.1.7`. This README documents the current feature set; consult the repository commits and releases for the exact changes included in each release.

## Previous changes

### v1.2.1

- Removes obsolete `sensor.airos_ethernet_ip_address` and `sensor.airos_ethernet_mac_address` entries from the Home Assistant entity registry during setup.
- Keeps the canonical Device IP Address and Device MAC Address sensors; existing cleanup logic is retained and the integration version is aligned for the v1.2.1 release.

### v1.2.0

- Standardizes user-facing wired-interface terminology to LAN in sensor labels, child-device names, model labels, and documentation.
- Preserves internal sensor keys and entity unique IDs for compatibility with existing Home Assistant entities and history.

### v1.1.9

- Removes duplicate LAN RX Errors and LAN TX Errors entities when the same counters are already exposed as LAN Receive Errors and LAN Transmit Errors.
- Removes obsolete LAN-specific IP and MAC entities while retaining the canonical Device IP Address and Device MAC Address sensors.

### v1.1.8

- Migrates the LAN IP sensor to `sensor.airos_device_ip_address`.
- Migrates the LAN MAC sensor to `sensor.nanostation5_ethernet_nanostation5_device_mac_address`.

### v1.1.7

- Removes the device model/name prefix (for example, `NanoStation5`) from sensor display names while retaining device grouping and the device name itself.
- Gives legacy LAN fields clear LAN names, including link status, received/transmitted data, packets, and errors.

### v1.1.6

- Adds LAN receive/transmit packet and error counters.
- Labels LAN byte counters as LAN Received Data and LAN Transmitted Data.
- Exposes LAN State as ON/OFF and groups LAN/IP/MAC-related sensors under the LAN device.
- Avoids a duplicate LAN MAC entity by using Device MAC Address.

### v1.1.5

- Standardizes the device hostname sensor as `sensor.airos_hostname`.
- Migrates existing `side_devicename` / `devicename` entity IDs to the canonical hostname entity ID when it is available, while preserving the entity unique ID.

## Features

- SSH polling of `mca-status`
- Wireless signal, noise, CCQ, SNR, and TX/RX rate monitoring
- Best-effort additional diagnostics from legacy BusyBox/procfs commands, including uptime, memory, CPU usage/model, firmware information, and load/system data where supported
- Device identity and network information, including hostname, IP/MAC addresses, and firmware metadata
- LAN, wireless, and PPP interface counters when exposed by the device
- Reboot switch
- Home Assistant Config Flow (UI setup)
- HACS compatibility

Sensor availability varies by model and firmware. Some older airOS versions do not expose every command, file, or counter; optional probes are best-effort.

## Installation (manual)

1. Download this repository.
2. Copy `custom_components/airos_xs2` into your Home Assistant `/config/custom_components/` directory.
3. Restart Home Assistant.
4. Go to **Settings → Devices & Services → Add Integration** and select **Ubiquiti AirOS (SSH)**.
5. Enter the radio's IP address and SSH credentials.

## Installation (HACS)

1. Open **HACS → Integrations → ⋮ → Custom repositories**.
2. Add `https://github.com/jonny5509/ha-airos-ssh`.
3. Select **Integration** as the category.
4. Install the integration and restart Home Assistant.
5. Add it from **Settings → Devices & Services → Add Integration**.

## Security and compatibility

- Designed for legacy Ubiquiti AirOS firmware 4.x and related older devices.
- Uses legacy SSH key-exchange, cipher, and host-key algorithms required by some older firmware.
- The current connection configuration disables known-host verification (`known_hosts=None`). Use only on a trusted network; this does not authenticate the radio's host key.
- Use a trusted LAN or VPN and avoid exposing the device's management interface to the public internet.

## Branding

The integration includes its own Home Assistant brand assets in `custom_components/airos_xs2/brand/`:

- `icon.png` — standard 256 × 256 icon
- `icon@2x.png` — high-resolution 512 × 512 icon

Home Assistant 2026.3 and newer can serve these local brand assets directly after the integration is installed. HACS Marketplace branding may use the separate brand-image publishing flow. The artwork is for identification and is not an official Home Assistant brand.

## Validation

GitHub Actions runs Home Assistant `hassfest` validation and HACS integration validation on pushes and pull requests.

## License

MIT License

## Related project

The separate HTTP-based integration is available at https://github.com/jonny5509/ha-airos-http. The HTTP and SSH variants use different transports and may expose different sensors.
