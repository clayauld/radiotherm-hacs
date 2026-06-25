"""The Radio Thermostat integration data."""

from dataclasses import dataclass
from typing import Any, Optional, cast

import radiotherm
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from radiotherm.thermostat import CommonThermostat

from .const import TIMEOUT


@dataclass
class RadioThermUpdate:
    """An update from a Radio Thermostat device."""

    tstat: dict[str, Any]
    humidity: Optional[int]


@dataclass
class RadioThermInitData:
    """An data needed to init the integration."""

    tstat: CommonThermostat
    host: str
    name: str
    mac: str
    model: Optional[str]
    fw_version: Optional[str]
    api_version: Optional[int]


def _get_init_data(host: str) -> RadioThermInitData:
    tstat = radiotherm.get_thermostat(host)
    tstat.timeout = TIMEOUT
    name: str = tstat.name["raw"]
    sys: dict[str, Any] = tstat.sys["raw"]
    mac: str = dr.format_mac(sys["uuid"])
    model: str = tstat.model.get("raw")
    return RadioThermInitData(
        tstat, host, name, mac, model, sys.get("fw_version"), sys.get("api_version")
    )


async def async_get_init_data(hass: HomeAssistant, host: str) -> RadioThermInitData:
    """Get the RadioInitData."""
    return cast(
        RadioThermInitData, await hass.async_add_executor_job(_get_init_data, host)
    )


def _get_data(device: CommonThermostat) -> RadioThermUpdate:
    # Request the current state from the thermostat.
    # Radio thermostats are very slow, and sometimes don't respond
    # very quickly.  So we need to keep the number of calls to them
    # to a bare minimum or we'll hit the Home Assistant 10 sec warning.  We
    # have to make one call to /tstat to get temps but we'll try and
    # keep the other calls to a minimum.  Even with this, these
    # thermostats tend to time out sometimes when they're actively
    # heating or cooling.
    tstat: dict[str, Any] = device.tstat["raw"]
    humidity: Optional[int] = None
    if isinstance(device, radiotherm.thermostat.CT80):
        humidity = device.humidity["raw"]
    return RadioThermUpdate(tstat, humidity)


async def async_get_data(
    hass: HomeAssistant, device: CommonThermostat
) -> RadioThermUpdate:
    """Fetch the data from the thermostat."""
    return cast(RadioThermUpdate, await hass.async_add_executor_job(_get_data, device))
