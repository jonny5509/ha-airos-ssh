from custom_components.airos_xs2.coordinator import (
    AiRXS2Coordinator,
    _number,
    _to_text,
)


def test_to_text_handles_bytes_and_none():
    assert _to_text(b"signal=-65") == "signal=-65"
    assert _to_text(None) == ""
    assert _to_text("already text") == "already text"


def test_number_returns_default_for_invalid_values():
    assert _number("12.5") == 12.5
    assert _number("not a number", default=-1) == -1
    assert _number(None) is None


def test_parse_output_parses_values_and_calculates_snr_and_ccq():
    coordinator = object.__new__(AiRXS2Coordinator)

    data = coordinator._parse_output(
        "signal=-65\nnoise=-95\nccq=950\nwlanTxRate=54\nwlanRxRate=48\n"
    )

    assert data["signal"] == -65
    assert data["noise"] == -95
    assert data["snr"] == 30
    assert data["ccq"] == 95
    assert data["wlanTxRate"] == 54
    assert data["wlanRxRate"] == 48


def test_parse_output_preserves_values_containing_equals():
    coordinator = object.__new__(AiRXS2Coordinator)

    data = coordinator._parse_output("custom=value=with=equals\n")

    assert data["custom"] == "value=with=equals"


def test_identify_device_recognizes_nano_station_models():
    ns2 = {"platform": "XS2"}
    ns5 = {"platform": "XS5"}

    AiRXS2Coordinator._identify_device(ns2)
    AiRXS2Coordinator._identify_device(ns5)

    assert ns2["device_model"] == "NanoStation2"
    assert ns5["device_model"] == "NanoStation5"


def test_identify_device_does_not_classify_other_families_as_nano_station():
    loco = {"platform": "NanoStation Loco5"}
    powerstation = {"platform": "PowerStation2"}

    AiRXS2Coordinator._identify_device(loco)
    AiRXS2Coordinator._identify_device(powerstation)

    assert loco["device_model"] != "NanoStation5"
    assert powerstation["device_model"] != "NanoStation2"


def test_firmware_status_compares_supported_nano_station_5_versions():
    older = {"device_model": "NanoStation5", "firmwareVersion": "v4.0.3"}
    current = {"device_model": "NanoStation5", "firmwareVersion": "v4.0.4.5074"}
    unsupported = {"device_model": "NanoStation2", "firmwareVersion": "v4.0.4"}

    AiRXS2Coordinator._update_firmware_upgrade_status(older)
    AiRXS2Coordinator._update_firmware_upgrade_status(current)
    AiRXS2Coordinator._update_firmware_upgrade_status(unsupported)

    assert older["firmware_upgrade"] == "Update available"
    assert current["firmware_upgrade"] == "Up to date"
    assert unsupported["firmware_upgrade"] == "Unknown"
    assert unsupported["firmware_upgrade_latest_version"] == "4.0.4.5074"


def test_uptime_probe_parses_proc_uptime():
    coordinator = object.__new__(AiRXS2Coordinator)
    data = {}

    coordinator._parse_probe("uptime", "1234.56 789.00", data)

    assert data["uptime_seconds"] == 1234.56


def test_meminfo_probe_calculates_ram_usage_using_mem_available():
    coordinator = object.__new__(AiRXS2Coordinator)
    data = {}

    coordinator._parse_probe(
        "meminfo",
        "MemTotal: 1000 kB\nMemFree: 200 kB\nMemAvailable: 400 kB\n",
        data,
    )

    assert data["mem_total_bytes"] == 1_024_000
    assert data["mem_free_bytes"] == 204_800
    assert data["mem_available_bytes"] == 409_600
    assert data["ram_usage_percent"] == 60.0


def test_cpu_stat_probe_uses_two_samples_to_calculate_usage():
    coordinator = object.__new__(AiRXS2Coordinator)
    coordinator._previous_cpu_stats = None
    data = {}

    coordinator._parse_probe("cpu_stat", "cpu 100 0 50 850\n", data)
    assert "cpu_usage" not in data

    coordinator._parse_probe("cpu_stat", "cpu 150 0 75 875\n", data)

    assert data["cpu_usage"] == 75.0
