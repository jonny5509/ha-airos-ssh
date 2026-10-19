# Ubiquiti AirOS (SSH)

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

Home Assistant 2026.3 and newer supports integration brand images shipped in the integration's `brand/` directory. The `custom_components/airos_xs2/brand/README.md` documents the intended assets. The PNG image files still need to be added before the integration has its own logo/icon.

## Compatibility

- Ubiquiti AirOS firmware 4.x
- Uses legacy SSH algorithms required by older firmware

## License

MIT License
