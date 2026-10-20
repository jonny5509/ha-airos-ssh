# Changelog

This changelog records verified changes from the available repository history. It is not a complete reconstruction of every historical release.

## 2.1.8

- Align the setup form's field labels, default device name, and host example with the HTTP integration.
- Clarify the SSH connection details while retaining SSH-specific credential descriptions.

## 2.1.7

- Align diagnostic sensor coverage with the HTTP integration where SSH commands expose the relevant values.
- Remove duplicate sensor aliases to avoid creating duplicate entities for equivalent status fields.
- Add automated tests for coordinator parsing and system-stat probes.
- Add a GitHub Actions workflow to run the test suite on pushes and pull requests.
- Update installation, compatibility, and security documentation.

## Notes

- Sensor availability varies by device model and firmware; optional diagnostic probes are best-effort.
- Older devices may require legacy SSH algorithms.
- The current connection configuration does not verify the server host key. Use only on a trusted LAN or VPN and do not expose the radio's management interface to the public internet.
- Review the repository's [README](README.md) for current installation, compatibility, troubleshooting, and security guidance.
