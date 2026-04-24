"""Config flow voor de Financieel Beheer integratie."""
import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_URL, CONF_TOKEN
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL, description={"suggested_value": "http://homeassistant.local:8099"}): str,
        vol.Required(CONF_TOKEN): str,
    }
)


class HaFinanceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow voor Financieel Beheer."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            url = user_input[CONF_URL].rstrip("/")
            token = user_input[CONF_TOKEN]

            try:
                session = async_get_clientsession(self.hass)
                async with session.get(
                    f"{url}/api/integration/stats",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 401:
                        errors["token"] = "invalid_token"
                    elif resp.status == 503:
                        errors["base"] = "token_not_configured"
                    elif resp.status != 200:
                        errors["base"] = "cannot_connect"
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"

            if not errors:
                await self.async_set_unique_id(url)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Financieel Beheer",
                    data={CONF_URL: url, CONF_TOKEN: token},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )
