"""Config flow for the Ubiquiti AirOS SSH integration."""

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN


class AiRXS2ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle configuration of an AirOS SSH device."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial setup step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            name = user_input[CONF_NAME].strip()
            host = user_input[CONF_HOST].strip().rstrip(".").lower()
            username = user_input[CONF_USERNAME].strip()
            password = user_input[CONF_PASSWORD]

            if not host or not name or not username or not password:
                errors["base"] = "invalid_input"
            else:
                # Host/IP is not a stable device identifier. Prevent duplicate
                # manual entries by matching the normalized host in entry data.
                self._async_abort_entries_match({CONF_HOST: host})
                return self.async_create_entry(
                    title=name,
                    data={
                        **user_input,
                        CONF_NAME: name,
                        CONF_HOST: host,
                        CONF_USERNAME: username,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME): str,
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )
