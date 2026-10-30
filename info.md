# Ubiquiti AirOS (SSH)

Home Assistant custom integration for monitoring legacy Ubiquiti airOS 4.x radios over SSH, including NanoStation2, NanoStation5, PowerStation2, and related older hardware.

- **Domain:** `airos_xs2`
- **Current integration version:** `2.3.1`
- **Communication:** Local SSH polling using AsyncSSH; includes a reboot button
- **Documentation:** https://github.com/jonny5509/ha-airos-ssh
- **Issues:** https://github.com/jonny5509/ha-airos-ssh/issues
- **Related HTTP integration:** https://github.com/jonny5509/ha-airos-http

Features and sensor availability depend on the radio model, firmware, and commands or counters exposed by the device. Optional CPU, memory, load, and system diagnostic probes are best-effort.

**Security:** The current connection configuration does not verify the server host key, and some older devices may require legacy SSH algorithms. Use only on a trusted LAN or VPN and do not expose the radio's management interface to the public internet.

This integration is community-maintained and is not affiliated with Ubiquiti.