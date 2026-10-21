import asyncio
import asyncssh
import logging
import re
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant
from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


def _to_text(val) -> str:
    if val is None:
        return ""
    if isinstance(val, (bytes, bytearray)):
        return val.decode(errors="ignore")
    return str(val)


def _number(value, default=None):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class AiRXS2Coordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, host, username, password, name):
        self.host = host
        self.username = username
        self.password = password
        self.device_name = name
        self._previous_cpu_stats = None

        super().__init__(
            hass,
            logger=_LOGGER,
            name=f"airos_xs2_{name}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _run_command(self, conn, command):
        """Run a read-only command without relying on completed-result attributes."""
        async with conn.create_process(command) as proc:
            stdout = await proc.stdout.read()
            stderr = await proc.stderr.read()
            await proc.wait()
        output = _to_text(stdout)
        return output if output.strip() else _to_text(stderr)

    async def _async_update_data(self):
        try:
            async with asyncssh.connect(
                self.host,
                username=self.username,
                password=self.password,
                known_hosts=None,
                kex_algs=["diffie-hellman-group1-sha1"],
                encryption_algs=["aes128-cbc"],
                server_host_key_algs=["ssh-rsa"],
            ) as conn:
                output = await self._run_command(conn, "mca-status")
                if "=" not in output:
                    raise UpdateFailed(
                        f"mca-status returned no key=value output: {output[:200]}"
                    )
                data = self._parse_output(output)

                # Legacy airOS builds differ significantly. Probe common BusyBox
                # procfs/network commands independently; missing commands/files are
                # ignored so one unsupported probe cannot break the core sensors.
                probes = (
                    ("uptime", "cat /proc/uptime"),
                    ("meminfo", "cat /proc/meminfo"),
                    ("cpu_stat", "cat /proc/stat"),
                    ("cpu_top", "top -b -n2 -d1"),
                    ("cpuinfo", "cat /proc/cpuinfo"),
                    ("version", "cat /etc/version"),
                    ("board", "cat /etc/board.info"),
                    ("ifconfig", "ifconfig"),
                    ("netdev", "cat /proc/net/dev"),
                )
                for name, command in probes:
                    try:
                        result = await self._run_command(conn, command)
                        self._parse_probe(name, result, data)

                        # Very old airOS kernels (including XS5 v4.x) expose only
                        # four /proc/stat counters. The first sample establishes a
                        # baseline, so take a second sample immediately rather than
                        # leaving CPU Usage unknown until the next HA polling cycle.
                        if name == "cpu_stat" and "cpu_usage" not in data:
                            await asyncio.sleep(1)
                            second_sample = await self._run_command(conn, "cat /proc/stat")
                            self._parse_probe("cpu_stat", second_sample, data)
                    except Exception as err:
                        _LOGGER.debug("airOS probe %s unavailable: %s", name, err)

                self._update_firmware_upgrade_status(data)
                return data

        except UpdateFailed:
            raise
        except Exception as e:
            raise UpdateFailed(f"SSH error: {e}") from e

    def _parse_output(self, output: str):
        data = {}
        for line in output.splitlines():
            if "=" in line:
                key, value = line.strip().split("=", 1)
                data[key] = value.strip()

        # Some legacy AirOS versions bundle identity metadata into side_devicename,
        # e.g. "UBNT,deviceId=...,firmwareVersion=...,platform=...,deviceIp=...".
        # Split those fields into their own values so Home Assistant can expose
        # them as individual sensors instead of hiding them in the name sensor.
        for key, value in list(data.items()):
            # Depending on the AirOS generation, identity metadata is returned
            # under side_devicename or deviceName. Both may contain a comma-
            # separated metadata blob rather than just a human-readable name.
            if key.lower() not in {"side_devicename", "devicename"}:
                continue
            parts = [part.strip() for part in value.split(",")]
            data[key] = parts[0] or "AirOS Device"
            metadata_keys = {
                "deviceid": "deviceId",
                "firmwareversion": "firmwareVersion",
                "platform": "platform",
                "deviceip": "deviceIp",
            }
            for part in parts[1:]:
                if "=" not in part:
                    continue
                metadata_key, metadata_value = part.split("=", 1)
                canonical_key = metadata_keys.get(metadata_key.strip().lower())
                metadata_value = metadata_value.strip()
                if canonical_key and metadata_value:
                    data.setdefault(canonical_key, metadata_value)

            # Keep the legacy side_devicename entity ID working if the device
            # reports its name using the newer deviceName key.
            if key.lower() == "devicename":
                data.setdefault("side_devicename", data[key])
                data.pop(key, None)

        # Canonicalise firmware-specific spellings into stable main-device sensors.
        lookup = {re.sub(r"[^a-z0-9]", "", str(k).lower()): v for k, v in data.items()}
        aliases = {
            "firmwareVersion": ("firmwareVersion", "firmware_version", "fwversion", "firmware", "version"),
            "apmac": ("apmac","ap_mac","apmacaddr","wlan_apmac"),
            "cfg_crc": ("cfgcrc","cfg_crc","configcrc","config_crc"),
            "distance": ("distance","linkdistance","dist"),
            "ack_timeout": ("acktimeout","ack_timeout"),
            "latitude": ("latitude","lat"), "longitude": ("longitude","lon","lng"),
            "radio_date_time": ("datetime","radio_datetime","date_time","radio_date_time"),
            "ppp_ip": ("pppip","ppp_ip","pppaddress"),
        }
        for target, candidates in aliases.items():
            for candidate in candidates:
                value = lookup.get(re.sub(r"[^a-z0-9]", "", candidate))
                if value not in (None, ""):
                    data.setdefault(target, value)
                    break

        # Keep installed firmware under one canonical key. Prefer explicit
        # firmware fields, but accept legacy status.cgi/mca-status spellings.
        if data.get("firmwareVersion") not in (None, ""):
            for alias in ("firmware_version", "fwversion", "firmware", "version"):
                alias_key = next(
                    (key for key in data if re.sub(r"[^a-z0-9]", "", str(key).lower())
                     == re.sub(r"[^a-z0-9]", "", alias)),
                    None,
                )
                if alias_key is not None and alias_key != "firmwareVersion":
                    data.pop(alias_key, None)
        self._identify_device(data, output)

        # Expose only one canonical uptime sensor, populated by the procfs probe.
        # airOS firmware may also report uptime-like keys in mca-status; discard
        # those aliases so they cannot create duplicate entities.
        for key in list(data):
            if key.lower() in {"uptime", "uptime_seconds", "systemuptime"}:
                data.pop(key, None)

        # Missing or malformed readings must stay unavailable, not look like real zeroes.
        for key in ("signal", "noise", "wlanTxRate", "wlanRxRate", "frequency"):
            value = _number(data.get(key))
            if value is None:
                data.pop(key, None)
            else:
                data[key] = value

        raw_ccq = _number(data.get("ccq"))
        if raw_ccq is None:
            data.pop("ccq", None)
        else:
            # AirOS mca-status reports CCQ in tenths of a percent.
            data["ccq"] = raw_ccq / 10

        if "signal" in data and "noise" in data:
            data["snr"] = data["signal"] - data["noise"]
        else:
            data.pop("snr", None)
        return data

    @staticmethod
    def _identify_device(data, extra_output=""):
        """Identify original airOS 3.x-4.x hardware from legacy metadata."""
        identity_keys = {
            "platform", "deviceid", "board", "boardname", "board_name",
            "product", "productname", "model", "devicemodel", "hardware",
        }
        parts = [extra_output]
        for key, value in data.items():
            if (key.lower() in identity_keys or key.lower() in {"firmwareversion", "cpu_model"}\n                    or key.lower().endswith(("_platform", "_deviceid", "_board", "_boardname", "_product", "_productname", "_model", "_devicemodel", "_hardware", "_firmwareversion"))):
                parts.append(str(value))
        identity = " ".join(parts)
        compact = re.sub(r"[^a-z0-9]", "", identity.lower())

        # Prefer explicit product identifiers. XS2/XS5 firmware prefixes are
        # only a fallback because several original airOS products share them.
        model_aliases = (
            ("nanostationloco2", "NanoStation Loco2"),
            ("nanostationloco5", "NanoStation Loco5"),
            ("loco2", "NanoStation Loco2"),
            ("loco5", "NanoStation Loco5"),
            ("picostation2", "PicoStation 2"),
            ("picostation5", "PicoStation 5"),
            ("powerstation2", "PowerStation 2"),
            ("powerstation5", "PowerStation 5"),
            ("bullet2", "Bullet2"),
            ("bullet5", "Bullet5"),
            ("nanostation2", "NanoStation 2"),
            ("nanostation5", "NanoStation 5"),
            ("ns2", "NanoStation 2"),
            ("ns5", "NanoStation 5"),
        )
        for alias, label in model_aliases:
            if alias in compact:
                data["device_model"] = label
                return

        firmware = str(data.get("firmwareVersion") or "")
        if not firmware:
            firmware_match = re.search(r"(?i)\b(XS[25])\b", identity)
            firmware = firmware_match.group(1) if firmware_match else ""
        if firmware.upper().startswith("XS2") or re.search(r"(?i)\b(?:NS2|XS2)\b", identity):
            data["device_model"] = "NanoStation 2"
        elif firmware.upper().startswith("XS5") or re.search(r"(?i)\b(?:NS5|XS5)\b", identity):
            data["device_model"] = "NanoStation 5"
        else:
            for key in ("platform", "deviceId", "board", "board_name", "product", "model", "cpu_model"):
                value = data.get(key)
                if value and str(value).strip():
                    data["device_model"] = str(value).strip()
                    break

    @staticmethod
    def _update_firmware_upgrade_status(data):
        """Compare supported legacy NanoStation5 firmware with Ubiquiti's published release."""
        # Ubiquiti's published final legacy NanoStation5 release is v4.0.4
        # build 5074. Do not extrapolate this catalog entry to other models.
        data["firmware_upgrade_latest_version"] = "4.0.4.5074"
        data["firmware_upgrade_source"] = "https://ui.com/download/airmax-legacy"

        if data.get("device_model") != "NanoStation5":
            data["firmware_upgrade"] = "Unknown"
            data["firmware_upgrade_reason"] = "No verified firmware catalog entry for this device model."
            return

        installed = str(data.get("firmwareVersion") or "")
        match = re.search(r"v?(\d+)\.(\d+)\.(\d+)(?:\.(\d+))?", installed, re.IGNORECASE)
        if not match:
            data["firmware_upgrade"] = "Unknown"
            data["firmware_upgrade_reason"] = "Installed firmware version could not be parsed."
            return

        installed_version = tuple(int(part or 0) for part in match.groups())
        latest_version = (4, 0, 4, 5074)
        data["firmware_upgrade_installed_version"] = installed
        if installed_version < latest_version:
            data["firmware_upgrade"] = "Update available"
            data["firmware_upgrade_reason"] = "A newer published legacy NanoStation5 firmware version exists. Check release notes and upgrade prerequisites before installing."
        elif installed_version == latest_version:
            data["firmware_upgrade"] = "Up to date"
            data["firmware_upgrade_reason"] = "Installed version matches the published legacy NanoStation5 release."
        else:
            data["firmware_upgrade"] = "Unknown"
            data["firmware_upgrade_reason"] = "Installed version is newer than the catalog entry; automatic comparison is inconclusive."

    def _parse_probe(self, name, output, data):
        if not output:
            return

        if name == "uptime":
            match = re.match(r"\s*([0-9]+(?:\.[0-9]+)?)", output)
            if match:
                data["uptime_seconds"] = float(match.group(1))
        elif name == "meminfo":
            values = {}
            for line in output.splitlines():
                match = re.match(r"^(MemTotal|MemFree|MemAvailable):\s+(\d+)", line)
                if match:
                    values[match.group(1)] = int(match.group(2)) * 1024
            for source, target in (
                ("MemTotal", "mem_total_bytes"),
                ("MemFree", "mem_free_bytes"),
                ("MemAvailable", "mem_available_bytes"),
            ):
                if source in values:
                    data[target] = values[source]

            # Report a single percentage-based RAM sensor. Prefer MemAvailable,
            # which accounts for reclaimable cache; older kernels may only expose
            # MemFree, so use that as a fallback.
            total = data.get("mem_total_bytes")
            available = data.get("mem_available_bytes", data.get("mem_free_bytes"))
            if total and available is not None and total > 0:
                used_percent = (total - available) / total * 100
                data["ram_usage_percent"] = round(max(0.0, min(100.0, used_percent)), 2)
        elif name == "cpu_stat":
            # /proc/stat exposes cumulative CPU time counters. Compare consecutive
            # samples to calculate actual utilisation rather than load average.
            lines = output.splitlines()
            fields = lines[0].split() if lines else []
            if fields and fields[0] == "cpu" and len(fields) >= 5:
                try:
                    counters = [int(value) for value in fields[1:9]]
                except ValueError:
                    counters = []

                if len(counters) >= 4:
                    total = sum(counters)
                    idle = counters[3]
                    if len(counters) >= 5:
                        idle += counters[4]  # Treat I/O wait as idle time.

                    previous = self._previous_cpu_stats
                    self._previous_cpu_stats = (total, idle)
                    if previous is not None:
                        total_delta = total - previous[0]
                        idle_delta = idle - previous[1]
                        if total_delta > 0 and 0 <= idle_delta <= total_delta:
                            data["cpu_usage"] = round(
                                100 * (total_delta - idle_delta) / total_delta, 2
                            )
        elif name == "cpu_top":
            # Some older AirOS builds do not expose usable /proc/stat counters.
            # Fall back to the CPU summary printed by BusyBox top.
            if "cpu_usage" not in data:
                cpu_lines = [
                    line for line in output.splitlines()
                    if re.search(r"\bCPU\s*:", line, re.IGNORECASE)
                ]
                if cpu_lines:
                    values = {
                        label.lower(): float(value)
                        for value, label in re.findall(
                            r"(\d+(?:\.\d+)?)\s*%\s*([a-z]+)",
                            cpu_lines[-1],
                            re.IGNORECASE,
                        )
                    }
                    idle = values.get("idle")
                    if idle is not None:
                        # I/O wait is treated as idle; other reported categories
                        # (user, system, IRQ, softirq, nice) count as busy.
                        io_wait = values.get("io", 0.0)
                        usage = max(0.0, min(100.0, 100.0 - idle - io_wait))
                        data["cpu_usage"] = round(usage, 2)
        elif name == "version":
            # The legacy /etc/version file often contains the full firmware build,
            # even when mca-status does not expose firmwareVersion.
            if re.search(r"(?i)(?:XS[25]|NS[25]|NanoStation)", output) and re.search(r"\d+\.\d+\.\d+", output):
                data.setdefault("firmwareVersion", output.strip().splitlines()[0])
            self._identify_device(data, output)
        elif name == "board":
            # Some firmware exposes model/board identity in this file.
            self._identify_device(data, output)
        elif name == "cpuinfo":
            for line in output.splitlines():
                if ":" in line and line.split(":", 1)[0].strip().lower() in (
                    "system type", "model name", "processor"
                ):
                    value = line.split(":", 1)[1].strip()
                    if value:
                        data["cpu_model"] = value
                        self._identify_device(data)
                        break
        elif name == "ifconfig":
            # Parse each interface separately; order varies by firmware.
            # Legacy airOS commonly uses ath0/wlan0, eth0, and br0.
            blocks = re.split(r"(?m)^(?=[A-Za-z0-9_.:-]+\s+Link encap:)", output)
            for block in blocks:
                heading = re.match(r"^([A-Za-z0-9_.:-]+)\s+Link encap:", block)
                if not heading:
                    continue
                interface = heading.group(1).lower()
                is_wireless = interface.startswith(("wlan", "ath"))
                is_ethernet = interface.startswith(("eth", "br"))
                is_ppp = interface.startswith("ppp")
                if not (is_wireless or is_ethernet or is_ppp):
                    continue
                prefix = "wireless" if is_wireless else ("ppp" if is_ppp else "ethernet")
                mac = re.search(r"(?:HWaddr|ether)\s+([0-9A-Fa-f:]{17})", block)
                if mac:
                    data.setdefault(f"{prefix}_mac", mac.group(1))
                    if is_ethernet:
                        data.setdefault("mac", mac.group(1))
                    if is_wireless:
                        data.setdefault("wlanMac", mac.group(1))
                ip = re.search(r"inet addr:([0-9.]+)", block)
                if not ip:
                    ip = re.search(r"\binet ([0-9.]+)", block)
                if ip:
                    data.setdefault("ip_address", ip.group(1))
                    if is_ppp:
                        data.setdefault("ppp_ip", ip.group(1))

                flags = re.search(r"<([^>]+)>", block)
                if flags:
                    state = "up" if "UP" in flags.group(1).split(",") else "down"
                    data.setdefault(f"{prefix}_interface_state", state)
                    if is_ethernet:
                        data["ethernet_interface_state"] = "ON" if state == "up" else "OFF"
                elif re.search(r"(?m)^\s*UP(?:\s|$)", block):
                    data.setdefault(f"{prefix}_interface_state", "up")
                    if is_ethernet:
                        data["ethernet_interface_state"] = "ON"
                elif re.search(r"(?m)^\s*DOWN(?:\s|$)", block):
                    data.setdefault(f"{prefix}_interface_state", "down")
                    if is_ethernet:
                        data["ethernet_interface_state"] = "OFF"

        elif name == "netdev":
            # Prefer physical interfaces to bridge aliases, avoiding br0 counters
            # being mislabeled as the physical Ethernet port when eth0 is present.
            counters = {}
            for line in output.splitlines():
                if ":" not in line:
                    continue
                interface, stats = line.split(":", 1)
                interface = interface.strip().lower()
                values = stats.split()
                if len(values) < 11:
                    continue
                if interface.startswith(("wlan", "ath")):
                    prefix, priority = "wireless", 2
                elif interface.startswith("ppp"):
                    prefix, priority = "ppp", 2
                elif interface.startswith("eth"):
                    prefix, priority = "ethernet", 2
                elif interface.startswith("br"):
                    prefix, priority = "ethernet", 1
                else:
                    continue
                try:
                    rx_bytes = int(values[0])
                    rx_packets = int(values[1])
                    rx_errors = int(values[2])
                    tx_bytes = int(values[8])
                    tx_packets = int(values[9])
                    tx_errors = int(values[10])
                except (TypeError, ValueError, IndexError):
                    _LOGGER.debug("Skipping malformed /proc/net/dev row: %s", line)
                    continue
                previous = counters.get(prefix)
                if previous is None or priority > previous[0]:
                    counters[prefix] = (
                        priority, rx_bytes, rx_packets, rx_errors,
                        tx_bytes, tx_packets, tx_errors,
                    )
            for prefix, values in counters.items():
                _, rx_bytes, rx_packets, rx_errors, tx_bytes, tx_packets, tx_errors = values
                data[f"{prefix}_rx_bytes"] = rx_bytes
                data[f"{prefix}_tx_bytes"] = tx_bytes
                if prefix == "ethernet":
                    data["lan_rx_packets"] = rx_packets
                    data["lan_rx_errors"] = rx_errors
                    data["lan_tx_packets"] = tx_packets
                    data["lan_tx_errors"] = tx_errors
                elif prefix == "ppp":
                    data["ppp_rx_bytes"] = rx_bytes
                    data["ppp_rx_packets"] = rx_packets
                    data["ppp_rx_errors"] = rx_errors
                    data["ppp_tx_bytes"] = tx_bytes
                    data["ppp_tx_packets"] = tx_packets
                    data["ppp_tx_errors"] = tx_errors