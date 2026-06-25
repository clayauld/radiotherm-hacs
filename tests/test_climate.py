"""Test climate platform of Radio Thermostat integration."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import radiotherm

from custom_components.radiotherm.climate import (
    PRESET_HOME,
    ClimateEntityFeature,
    HVACMode,
    RadioThermostat,
)


@pytest.fixture
def mock_coordinator():
    """Mock RadioTherm update coordinator."""
    coordinator = MagicMock()
    coordinator.hass = MagicMock()
    coordinator.hass.async_add_executor_job = AsyncMock(
        side_effect=lambda func, *args: func(*args)
    )

    mock_init_data = MagicMock()
    mock_init_data.name = "Living Room"
    mock_init_data.model = "CT30"
    mock_init_data.mac = "00:11:22:33:44:55"
    mock_init_data.fw_version = "1.0"
    mock_init_data.tstat = MagicMock(spec=radiotherm.thermostat.CommonThermostat)

    coordinator.init_data = mock_init_data
    coordinator.data = MagicMock()
    # Initial state data
    coordinator.data.tstat = {
        "hold": 0,
        "temp": 72.0,
        "fmode": 0,  # Auto
        "fstate": 0,  # Off
        "tmode": 0,  # Off
        "tstate": 0,  # Idle
        "t_cool": 78.0,
        "t_heat": 68.0,
    }
    coordinator.data.humidity = None
    coordinator.async_request_refresh = AsyncMock()

    return coordinator


def test_radiothermostat_init_ct30(mock_coordinator):
    """Test climate entity initialization for CT30 (non-CT80)."""
    mock_coordinator.init_data.model = "CT30"

    # Ensure it's not a CT80 thermostat
    mock_coordinator.init_data.tstat = MagicMock(spec=radiotherm.thermostat.CT30)

    with patch(
        "custom_components.radiotherm.climate.radiotherm.thermostat.CT80",
        new=radiotherm.thermostat.CT80,
    ):
        entity = RadioThermostat(mock_coordinator)

        assert entity.unique_id == "00:11:22:33:44:55"
        # Features should include target temperature, fan mode, turn off, turn on
        expected_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.FAN_MODE
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.TURN_ON
        )
        assert entity.supported_features == expected_features
        assert entity.fan_modes == ["on", "auto"]
        assert not hasattr(entity, "preset_modes") or entity.preset_modes is None


def test_radiothermostat_init_ct80(mock_coordinator):
    """Test climate entity initialization for CT80."""
    mock_coordinator.init_data.model = "CT80"
    mock_coordinator.init_data.tstat = MagicMock(spec=radiotherm.thermostat.CT80)
    mock_coordinator.data.tstat["program_mode"] = 0

    with patch(
        "custom_components.radiotherm.climate.radiotherm.thermostat.CT80",
        new=radiotherm.thermostat.CT80,
    ):
        entity = RadioThermostat(mock_coordinator)

        expected_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.FAN_MODE
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.TURN_ON
            | ClimateEntityFeature.PRESET_MODE
        )
        assert entity.supported_features == expected_features
        assert "circulate" in entity.fan_modes
        assert entity.preset_modes == [
            "default",
            "home",
            "alternate",
            "away",
            "holiday",
        ]


@pytest.mark.asyncio
async def test_async_set_fan_mode(mock_coordinator):
    """Test setting fan mode."""
    entity = RadioThermostat(mock_coordinator)

    await entity.async_set_fan_mode("on")
    assert entity.fan_mode == "on"
    # Mapping "on" to code 2
    assert entity.device.fmode == 2
    mock_coordinator.async_request_refresh.assert_called_once()


@pytest.mark.asyncio
async def test_async_set_temperature_cool(mock_coordinator):
    """Test setting temperature in cool mode."""
    entity = RadioThermostat(mock_coordinator)
    # Set mock state to Cool
    entity._attr_hvac_mode = HVACMode.COOL

    await entity.async_set_temperature(temperature=75)
    assert entity.target_temperature == 75
    assert entity.device.t_cool == 75
    mock_coordinator.async_request_refresh.assert_called_once()


@pytest.mark.asyncio
async def test_async_set_temperature_heat(mock_coordinator):
    """Test setting temperature in heat mode."""
    entity = RadioThermostat(mock_coordinator)
    # Set mock state to Heat
    entity._attr_hvac_mode = HVACMode.HEAT

    await entity.async_set_temperature(temperature=69)
    assert entity.target_temperature == 69
    assert entity.device.t_heat == 69


@pytest.mark.asyncio
async def test_async_set_hvac_mode(mock_coordinator):
    """Test setting HVAC mode."""
    entity = RadioThermostat(mock_coordinator)

    await entity.async_set_hvac_mode(HVACMode.COOL)
    assert entity.hvac_mode == HVACMode.COOL
    # Cool mode updates target temperature setting automatically
    assert entity.device.t_cool == entity.target_temperature


@pytest.mark.asyncio
async def test_async_set_preset_mode(mock_coordinator):
    """Test setting preset mode for CT80."""
    mock_coordinator.init_data.model = "CT80"
    mock_coordinator.init_data.tstat = MagicMock(spec=radiotherm.thermostat.CT80)
    mock_coordinator.data.tstat["program_mode"] = 0

    with patch(
        "custom_components.radiotherm.climate.radiotherm.thermostat.CT80",
        new=radiotherm.thermostat.CT80,
    ):
        entity = RadioThermostat(mock_coordinator)

        await entity.async_set_preset_mode(PRESET_HOME)
        assert entity.preset_mode == PRESET_HOME
        assert entity.device.program_mode == 0  # Mapping HOME to 0
