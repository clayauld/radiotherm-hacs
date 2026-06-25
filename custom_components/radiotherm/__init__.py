"""The Radio Thermostat integration."""

from collections.abc import Coroutine
from typing import Any, TypeVar, cast
from urllib.error import URLError

from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from radiotherm.validate import RadiothermTstatError

from .const import CONF_SYNC_TIME, DOMAIN
from .coordinator import RadioThermConfigEntry, RadioThermUpdateCoordinator
from .data import async_get_init_data
from .util import async_set_time

PLATFORMS: list[Platform] = [Platform.CLIMATE, Platform.SWITCH]


# Monkey patch versatile_thermostat to avoid TypeError when evaluating
# ClimateEntityFeature.TARGET_TEMPERATURE_RANGE in self.supported_features.
try:
    from custom_components.versatile_thermostat.underlyings import (
        UnderlyingClimate,
    )
    from homeassistant.components.climate import ClimateEntityFeature

    @property  # type: ignore[misc]
    def patched_supported_features(self: Any) -> ClimateEntityFeature:
        """Get supported features, casting raw ints to ClimateEntityFeature."""
        features = self.get_underlying_attribute("supported_features")
        if features is not None:
            return ClimateEntityFeature(features)
        return ClimateEntityFeature(0)

    UnderlyingClimate.supported_features = patched_supported_features
except Exception:  # pylint: disable=broad-except  # nosec B110
    pass


_T = TypeVar("_T")


async def _async_call_or_raise_not_ready(
    coro: Coroutine[Any, Any, _T], host: str
) -> _T:
    """Call a coro or raise ConfigEntryNotReady."""
    try:
        return await coro
    except RadiothermTstatError as ex:
        msg = f"{host} was busy (invalid value returned): {ex}"
        raise ConfigEntryNotReady(msg) from ex
    except TimeoutError as ex:
        msg = f"{host} timed out waiting for a response: {ex}"
        raise ConfigEntryNotReady(msg) from ex
    except (OSError, URLError) as ex:
        msg = f"{host} connection error: {ex}"
        raise ConfigEntryNotReady(msg) from ex


async def async_setup_entry(hass: HomeAssistant, entry: RadioThermConfigEntry) -> bool:
    """Set up Radio Thermostat from a config entry."""
    host = entry.data[CONF_HOST]
    init_coro = async_get_init_data(hass, host)
    init_data = await _async_call_or_raise_not_ready(init_coro, host)
    coordinator = RadioThermUpdateCoordinator(hass, entry, init_data)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def _async_update_listener(
    hass: HomeAssistant, entry: RadioThermConfigEntry
) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: RadioThermConfigEntry) -> bool:
    """Unload a config entry."""
    return cast(
        bool, await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    )
