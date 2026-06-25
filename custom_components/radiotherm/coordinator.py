"""Coordinator for radiotherm."""

import logging
from datetime import datetime, timedelta
from urllib.error import URLError

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util
from radiotherm.validate import RadiothermTstatError
from typing_extensions import TypeAlias, override

from .const import CONF_SYNC_TIME
from .data import RadioThermInitData, RadioThermUpdate, async_get_data
from .util import async_set_time

RadioThermConfigEntry: TypeAlias = ConfigEntry["RadioThermUpdateCoordinator"]

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=15)
SYNC_TIME_INTERVAL = timedelta(hours=24)


class RadioThermUpdateCoordinator(DataUpdateCoordinator[RadioThermUpdate]):
    """DataUpdateCoordinator to gather data for radio thermostats."""

    config_entry: RadioThermConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: RadioThermConfigEntry,
        init_data: RadioThermInitData,
    ) -> None:
        """Initialize DataUpdateCoordinator."""
        self.init_data = init_data
        self._description = f"{init_data.name} ({init_data.host})"
        self._last_time_sync: datetime | None = None
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=f"radiotherm {self.init_data.name}",
            update_interval=UPDATE_INTERVAL,
        )

    @override  # type: ignore[misc]
    async def _async_update_data(self) -> RadioThermUpdate:
        """Update data from the thermostat."""
        try:
            data = await async_get_data(self.hass, self.init_data.tstat)
        except RadiothermTstatError as ex:
            msg = f"{self._description} was busy (invalid value returned): {ex}"
            raise UpdateFailed(msg) from ex
        except TimeoutError as ex:
            msg = f"{self._description}) timed out waiting for a response: {ex}"
            raise UpdateFailed(msg) from ex
        except (OSError, URLError) as ex:
            msg = f"{self._description} connection error: {ex}"
            raise UpdateFailed(msg) from ex
        options = self.config_entry.options  # type: ignore[attr-defined]
        if options.get(CONF_SYNC_TIME, True):
            now = dt_util.utcnow()
            if (
                self._last_time_sync is None
                or now - self._last_time_sync > SYNC_TIME_INTERVAL
            ):
                _LOGGER.debug("Syncing time for %s", self._description)
                try:
                    await async_set_time(
                        self.hass, self.init_data.tstat, data.tstat.get("hold", False)
                    )
                    self._last_time_sync = now
                except Exception as ex:
                    _LOGGER.warning(
                        "Failed to sync time for %s: %s", self._description, ex
                    )

        return data
