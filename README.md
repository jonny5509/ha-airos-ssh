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
2. Copy the `custom_components/airos_xs2` directory into your Home Assistant `/config/custom_components/` directory. The final path must be `/config/custom_components/airos_xs2/manifest.json`.
3. Make sure `manifest.json` is directly inside `airos_xs2` (not inside a second nested `custom_components/airos_xs2` directory).
4. Restart Home Assistant.
5. Go to **Settings → Devices & Services → Add Integration** and select **Ubiquiti AirOS (SSH)**.

## Installation (HACS)

1. Open **HACS → Integrations → ⋮ → Custom repositories**.
2. Add `https://github.com/jonny5509/ha-airos-ssh`.
3. Select **Integration** as the category.
4. Install the integration and restart Home Assistant.
5. Add it from **Settings → Devices & Services → Add Integration**.

## Troubleshooting: “Integration 'airos_xs2' not found”

This error means Home Assistant cannot discover the custom integration. The integration domain is `airos_xs2`; it must match both the directory name and the `domain` field in `manifest.json`.

1. Check that `/config/custom_components/airos_xs2/manifest.json` exists.
2. Check that the manifest contains `"domain": "airos_xs2"`.
3. If using HACS, confirm the download completed, then restart Home Assistant (not just reload the integration).
4. If installing manually, copy the repository's `custom_components/airos_xs2` directory itself, not the repository root or a nested directory.
5. If the integration was previously installed under a different name or was deleted, remove the stale entry from **Settings → Devices & Services** after the integration is discoverable again, or restore the integration files and restart before removing the entry.

Useful terminal checks:

```bash
ls -la /config/custom_components/airos_xs2/
cat /config/custom_components/airos_xs2/manifest.json
```

If the files and domain are correct but Home Assistant still reports the integration as missing, check the startup logs for a manifest parsing error or a Python import error. A missing-integration message alone does not identify a code defect: Home Assistant must first be able to see the integration files on disk.

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
