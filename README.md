# Ubiquiti AirOS (SSH)

[![Downloads](https://img.shields.io/github/downloads/jonny5509/ha-airos-ssh/total?label=downloads)](https://github.com/jonny5509/ha-airos-ssh/releases)

**Version:** 2.3.1  
**Transport:** SSH  
**Repository:** https://github.com/jonny5509/ha-airos-ssh

A Home Assistant custom integration for monitoring the original Ubiquiti NanoStation 2 (NS2/XS2) and NanoStation 5 (NS5/XS5) running legacy airOS 3.x–4.x. This edition connects over SSH and runs read-only status commands, with a button to reboot the radio.

## Features

- Home Assistant UI setup
- Wireless signal, noise, CCQ, SNR, and TX/RX rate monitoring
- Device hostname, IP/MAC addresses, uptime, and firmware information
- Best-effort CPU, memory, load, and system diagnostics where supported
- LAN, wireless, and PPP interface counters when available
- Reboot button

Sensor availability depends on the radio model, firmware, and commands or counters exposed by the device. Optional diagnostic probes are best-effort.

## Compatibility

- Intended specifically for the original NanoStation 2 (NS2/XS2) and NanoStation 5 (NS5/XS5) with airOS 3.x–4.x.
- Other product families, including NanoStation Loco, Bullet, PicoStation, and PowerStation, are outside the supported scope.
- Uses `mca-status` and additional legacy BusyBox/procfs commands where available.
- Automated tests cover NS2/NS5 identity and representative airOS 3.x/4.x version strings; optional command availability varies by firmware.
- May require legacy SSH key-exchange, cipher, or host-key algorithms for older firmware. Physical-radio testing across every firmware build has not been completed.

## Installation

### HACS

1. Open **HACS → Integrations → ⋮ → Custom repositories**.
2. Add `https://github.com/jonny5509/ha-airos-ssh` and select **Integration**.
3. Install **Ubiquiti AirOS (SSH)** and restart Home Assistant.
4. Go to **Settings → Devices & services → Add integration** and select **Ubiquiti AirOS (SSH)**.

### Manual

1. Download or clone this repository.
2. Copy `custom_components/airos_xs2` into your Home Assistant `config/custom_components/` directory.
3. Restart Home Assistant.
4. Add **Ubiquiti AirOS (SSH)** from **Settings → Devices & services → Add integration**.
5. Enter the radio's IP address and SSH credentials.

The integration requires the `asyncssh` dependency declared in its manifest.

## Troubleshooting

- Confirm SSH access to the radio from the Home Assistant host.
- Check the configured IP address and credentials.
- Some older firmware does not support every diagnostic command or counter; missing optional sensors may be expected.
- Remove passwords, private keys, and other secrets before sharing logs.

## Security

The current SSH connection configuration disables known-host verification (`known_hosts=None`), so the radio's host key is not authenticated. Legacy SSH algorithms may also provide weaker security. Use only on a trusted LAN or VPN, and do not expose the radio's management interface to the public internet.

## Related project

Prefer polling through the radio's web interface instead? See the [Ubiquiti AirOS (HTTP) integration](https://github.com/jonny5509/ha-airos-http).
