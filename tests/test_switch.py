"""Test switch platform of Radio Thermostat integration."""

from unittest.mock import AsyncMock, MagicMock

import pytest
import radiotherm

from custom_components.radiotherm.switch import RadioThermHoldSwitch


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
    mock_init_data.tstat = MagicMock(spec=radiotherm.thermostat.CommonThermostat)

    coordinator.init_data = mock_init_data
    coordinator.data = MagicMock()
    coordinator.data.tstat = {
        "hold": 0,
        "temp": 72.0,
    }
    coordinator.async_request_refresh = AsyncMock()

    return coordinator


def test_hold_switch_init(mock_coordinator):
    """Test hold switch initialization."""
    switch = RadioThermHoldSwitch(mock_coordinator)

    assert switch.unique_id == "00:11:22:33:44:55_hold"
    assert switch.is_on is False
    assert switch.translation_key == "hold"


@pytest.mark.asyncio
async def test_hold_switch_turn_on(mock_coordinator):
    """Test turning the hold switch on."""
    switch = RadioThermHoldSwitch(mock_coordinator)

    await switch.async_turn_on()
    assert switch.is_on is True
    assert switch.device.hold == 1
    mock_coordinator.async_request_refresh.assert_called_once()


@pytest.mark.asyncio
async def test_hold_switch_turn_off(mock_coordinator):
    """Test turning the hold switch off."""
    switch = RadioThermHoldSwitch(mock_coordinator)
    # Set to on first
    switch.coordinator.data.tstat["hold"] = 1
    switch._process_data()
    assert switch.is_on is True

    await switch.async_turn_off()
    assert switch.is_on is False
    assert switch.device.hold == 0
    mock_coordinator.async_request_refresh.assert_called_once()
