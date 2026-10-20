import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN


def _device_schema(data=None):
    data = data or {}
    if data:
        host_field = vol.Required(
            "host", default=data.get("host", vol.UNDEFINED)
        )
    else:
        host_field = vol.Required(
            "host",
            description={"suggested_value": "192.168.1.20"},
        )

    return vol.Schema(
        {
            vol.Required("name", default=data.get("name", "NanoStation5")): str,
            host_field: str,
            vol.Required("username", default=data.get("username", vol.UNDEFINED)): str,
            vol.Required("password", default=data.get("password", vol.UNDEFINED)): str,
        }
    )


class AiRXS2ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=user_input["name"],
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=_device_schema(),
        )

    async def async_step_reconfigure(self, user_input=None):
        entry = self._get_reconfigure_entry()

        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                entry,
                data=user_input,
                title=user_input["name"],
            )
            await self.hass.config_entries.async_reload(entry.entry_id)
            return self.async_abort(reason="reconfigure_successful")

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_device_schema(entry.data),
        )
