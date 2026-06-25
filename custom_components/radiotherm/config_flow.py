"""Config flow for Radio Thermostat integration."""

import logging
from typing import Any, Optional
from urllib.error import URLError

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.service_info.dhcp import DhcpServiceInfo
from radiotherm.validate import RadiothermTstatError
from typing_extensions import override

from .const import CONF_SYNC_TIME, DOMAIN
from .data import RadioThermInitData, async_get_init_data

_LOGGER = logging.getLogger(__name__)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


async def validate_connection(hass: HomeAssistant, host: str) -> RadioThermInitData:
    """Validate the connection."""
    try:
        return await async_get_init_data(hass, host)
    except (TimeoutError, RadiothermTstatError, URLError, OSError) as ex:
        raise CannotConnect(f"Failed to connect to {host}: {ex}") from ex


class RadioThermConfigFlow(ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
    """Handle a config flow for Radio Thermostat."""

    VERSION = 1

    @staticmethod
    @callback  # type: ignore[misc]
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlow:
        """Create the options flow."""
        return RadioThermOptionsFlowHandler(config_entry)

    def __init__(self) -> None:
        """Initialize ConfigFlow."""
        self.discovered_ip: Optional[str] = None
        self.discovered_init_data: Optional[RadioThermInitData] = None

    @override  # type: ignore[misc]
    async def async_step_dhcp(
        self, discovery_info: DhcpServiceInfo
    ) -> ConfigFlowResult:
        """Discover via DHCP."""
        self._async_abort_entries_match({CONF_HOST: discovery_info.ip})
        try:
            init_data = await validate_connection(self.hass, discovery_info.ip)
        except CannotConnect:
            return self.async_abort(reason="cannot_connect")
        await self.async_set_unique_id(init_data.mac)
        self._abort_if_unique_id_configured(
            updates={CONF_HOST: discovery_info.ip}, reload_on_update=False
        )
        self.discovered_init_data = init_data
        self.discovered_ip = discovery_info.ip
        return await self.async_step_confirm()

    async def async_step_confirm(
        self, user_input: Optional[dict[str, Any]] = None
    ) -> ConfigFlowResult:
        """Attempt to confirm."""
        ip_address = self.discovered_ip
        init_data = self.discovered_init_data
        if ip_address is None or init_data is None:
            raise ValueError("IP address or initial data is missing")
        if user_input is not None:
            return self.async_create_entry(
                title=init_data.name,
                data={CONF_HOST: ip_address},
            )

        self._set_confirm_only()
        placeholders = {
            "name": init_data.name,
            "host": ip_address,
            "model": init_data.model or "Unknown",
        }
        self.context["title_placeholders"] = placeholders
        return self.async_show_form(
            step_id="confirm",
            description_placeholders=placeholders,
        )

    @override  # type: ignore[misc]
    async def async_step_user(
        self, user_input: Optional[dict[str, Any]] = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                init_data = await validate_connection(self.hass, user_input[CONF_HOST])
            except CannotConnect:
                errors[CONF_HOST] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(init_data.mac, raise_on_progress=False)
                self._abort_if_unique_id_configured(
                    updates={CONF_HOST: user_input[CONF_HOST]},
                    reload_on_update=False,
                )
                return self.async_create_entry(
                    title=init_data.name,
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_HOST): str}),
            errors=errors,
        )


class RadioThermOptionsFlowHandler(OptionsFlow):
    """Handle Radio Thermostat options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Optional[dict[str, Any]] = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SYNC_TIME,
                        default=self.config_entry.options.get(CONF_SYNC_TIME, True),
                    ): bool,
                }
            ),
        )
