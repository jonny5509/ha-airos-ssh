# Ubiquiti AirOS (SSH)

[![Downloads](https://img.shields.io/github/downloads/jonny5509/ha-airos-ssh/total?label=downloads)](https://github.com/jonny5509/ha-airos-ssh/releases) [![Version](https://img.shields.io/github/v/release/jonny5509/ha-airos-ssh?display_name=tag&sort=semver)](https://github.com/jonny5509/ha-airos-ssh/releases/latest) [![HACS Compatible](https://img.shields.io/badge/HACS-Compatible-41BDF5.svg)](https://hacs.xyz/)


Home Assistant custom integration for legacy Ubiquiti AirOS devices (NanoStation2, PowerStation2, etc).

## Features

- SSH polling of `mca-status`
- Signal, Noise, CCQ, SNR
- TX/RX rate monitoring
- Exposes additional `mca-status` key/value fields as sensors
- Best-effort uptime, memory, load average, CPU model, IP/MAC, and Ethernet/wireless byte counters
- Reboot switch
- Config Flow (UI install)
- HACS compatible

## Installation (manual)

1. Download this repository.
2. Copy `custom_components/airos_xs2` into your Home Assistant `/config/custom_components/` directory.
3. Restart Home Assistant.
4. Go to **Settings → Devices & Services → Add Integration** and select **Ubiquiti AirOS (SSH)**.

## Installation (HACS)

1. Open **HACS → Integrations → ⋮ → Custom repositories**.
2. Add `https://github.com/jonny5509/ha-airos-ssh`.
3. Select **Integration** as the category.
4. Install the integration and restart Home Assistant.
5. Add it from **Settings → Devices & Services → Add Integration**.

## Branding

The integration includes its own Home Assistant brand assets in `custom_components/airos_xs2/brand/`:

- `icon.png` — standard 256 × 256 icon
- `icon@2x.png` — high-resolution 512 × 512 icon

Home Assistant 2026.3 and newer can serve these local brand assets directly after the integration is installed. HACS Marketplace branding may use the separate brand-image publishing flow. The artwork is for identification and is not an official Home Assistant brand.

## Validation

GitHub Actions runs both Home Assistant `hassfest` validation and the HACS integration validation on pushes and pull requests.

## Compatibility

- Ubiquiti AirOS firmware 4.x
- Uses legacy SSH algorithms required by older firmware

## License

MIT License
