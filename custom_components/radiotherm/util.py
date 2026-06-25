"""Utils for radiotherm."""

import json
import logging

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from radiotherm.thermostat import CommonThermostat
from radiotherm.validate import validate_response

_LOGGER = logging.getLogger(__name__)


async def async_set_time(
    hass: HomeAssistant, device: CommonThermostat, hold: bool = False
) -> None:
    """Sync time to the thermostat."""
    await hass.async_add_executor_job(_set_time, device, hold)


def _set_time(device: CommonThermostat, hold: bool) -> None:
    """Set device time."""
    now = dt_util.now()
    time_data = {
        "day": now.weekday(),
        "hour": now.hour,
        "minute": now.minute,
    }

    # Try setting time via /sys/time which doesn't clear hold/override
    try:
        data = json.dumps(time_data).encode("utf-8")
        response = device.post("/sys/time", data)
        validate_response(response)
        _LOGGER.debug("Set thermostat time via /sys/time")
        return
    except Exception as ex:
        _LOGGER.debug(
            "Failed to set thermostat time via /sys/time, "
            "falling back to /tstat: %s",
            ex,
        )

    # Fallback to /tstat which is known to work but clears hold/override
    # Calling this clears any local temperature override and
    # reverts to the scheduled temperature.
    # To avoid regression, only do this if the thermostat is not in hold mode.
    if not hold:
        device.time = time_data
