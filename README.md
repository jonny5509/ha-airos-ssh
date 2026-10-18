# Ubiquiti AirOS (SSH)

Home Assistant custom integration for legacy Ubiquiti AirOS devices (NanoStation2, PowerStation2, etc). For the HTTP-only variant, see [ha-airos-http](https://github.com/jonny5509/ha-airos-http).

## Features

- SSH polling of `mca-status`
- Signal, Noise, CCQ, SNR
- TX/RX rate monitoring
- Exposes all additional `mca-status` key/value fields as sensors
- Best-effort uptime, memory, load average, CPU model, IP/MAC, and Ethernet/wireless byte counters from common BusyBox/procfs commands (unsupported probes are skipped)
- Reboot switch
- Config Flow (UI install)
- HACS compatible

---

## Installation (Manual)

1. Download this repository.
2. Copy `custom_components/airos_xs2` into your Home Assistant `/config/custom_components/` directory.
3. Restart Home Assistant.
4. Add integration via **Settings → Devices & Services → Add Integration**.

---

## Installation (HACS)

1. Open **HACS → Integrations → ⋮ → Custom repositories**.
2. Add `https://github.com/jonny5509/ha-airos-ssh`.
3. Select **Integration** as the category.
4. If HACS asks for a branch, select `main`. Do not enter a short commit hash (for example, `5544ed9`) as a branch name.
5. Install the integration and restart Home Assistant.

### Troubleshooting HACS download errors

If the Home Assistant log says HACS is trying to download a URL like
`.../archive/refs/heads/5544ed9.zip` and receives a 404, HACS is treating
`5544ed9` as a branch name, but that branch may not exist. In HACS, remove
the incorrect custom-repository entry and add this repository again, making
sure the selected branch is `main`. Then retry the download.

This HACS configuration issue is separate from SSH connection or `mca-status`
errors reported after the integration loads.

---

## Branding

The SSH and [HTTP integration](https://github.com/jonny5509/ha-airos-http) use the same AirOS brand artwork so they appear consistently in Home Assistant. The PNG assets are stored in `custom_components/airos_xs2/brand/`:

- `icon.png` — 256 × 256 px
- `icon@2x.png` — 512 × 512 px

The artwork is maintained in the repository; no separate logo upload in HACS is required. See [the brand asset notes](custom_components/airos_xs2/brand/README.md).

---

## Screenshots

These screenshots are shared with the HTTP integration and illustrate the Home Assistant integration/device presentation.

![Overview](docs/screenshots/Screenshot1.png)
![Coop Radio](docs/screenshots/Screenshot2.png)
![Shed Radio](docs/screenshots/Screenshot3.png)

---

## Compatibility

- Ubiquiti AirOS firmware 4.x
- Uses legacy SSH algorithms required by older firmware

---

## License

[MIT License](LICENSE)
