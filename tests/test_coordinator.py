"""Test coordinator of Radio Thermostat integration."""

from unittest.mock import MagicMock, patch, AsyncMock
import pytest

from radiotherm.validate import RadiothermTstatError
from custom_components.radiotherm.coordinator import (
    RadioThermUpdateCoordinator,
    UPDATE_INTERVAL,
)
from custom_components.radiotherm.data import RadioThermUpdate
from homeassistant.helpers.update_coordinator import UpdateFailed


@pytest.fixture
def mock_hass():
    """Mock Home Assistant."""
    hass = MagicMock()
    hass.async_add_executor_job = AsyncMock(side_effect=lambda func, *args: func(*args))
    return hass


@pytest.fixture
def mock_init_data():
    """Mock initialization data."""
    init_data = MagicMock()
    init_data.name = "Living Room"
    init_data.host = "192.168.1.100"
    init_data.tstat = MagicMock()
    return init_data


@pytest.mark.asyncio
async def test_coordinator_init(mock_hass, mock_init_data):
    """Test coordinator initialization."""
    entry = MagicMock()
    coordinator = RadioThermUpdateCoordinator(mock_hass, entry, mock_init_data)

    assert coordinator.name == "radiotherm Living Room"
    assert coordinator.update_interval == UPDATE_INTERVAL
    assert coordinator.init_data == mock_init_data


@pytest.mark.asyncio
async def test_coordinator_update_data_success(mock_hass, mock_init_data):
    """Test successful data update."""
    entry = MagicMock()
    coordinator = RadioThermUpdateCoordinator(mock_hass, entry, mock_init_data)

    mock_update = RadioThermUpdate(tstat={"temp": 72.0}, humidity=45)

    with patch(
        "custom_components.radiotherm.coordinator.async_get_data",
        AsyncMock(return_value=mock_update),
    ) as mock_get_data:
        result = await coordinator._async_update_data()

        assert result == mock_update
        mock_get_data.assert_called_once_with(mock_hass, mock_init_data.tstat)


@pytest.mark.asyncio
async def test_coordinator_update_data_tstat_error(mock_hass, mock_init_data):
    """Test update when RadiothermTstatError is raised."""
    entry = MagicMock()
    coordinator = RadioThermUpdateCoordinator(mock_hass, entry, mock_init_data)

    with patch(
        "custom_components.radiotherm.coordinator.async_get_data",
        AsyncMock(side_effect=RadiothermTstatError("Busy")),
    ):
        with pytest.raises(UpdateFailed) as excinfo:
            await coordinator._async_update_data()
        assert "was busy" in str(excinfo.value)


@pytest.mark.asyncio
async def test_coordinator_update_data_timeout(mock_hass, mock_init_data):
    """Test update when TimeoutError is raised."""
    entry = MagicMock()
    coordinator = RadioThermUpdateCoordinator(mock_hass, entry, mock_init_data)

    with patch(
        "custom_components.radiotherm.coordinator.async_get_data",
        AsyncMock(side_effect=TimeoutError("Timeout")),
    ):
        with pytest.raises(UpdateFailed) as excinfo:
            await coordinator._async_update_data()
        assert "timed out" in str(excinfo.value)


@pytest.mark.asyncio
async def test_coordinator_update_data_connection_error(mock_hass, mock_init_data):
    """Test update when OSError is raised."""
    entry = MagicMock()
    coordinator = RadioThermUpdateCoordinator(mock_hass, entry, mock_init_data)

    with patch(
        "custom_components.radiotherm.coordinator.async_get_data",
        AsyncMock(side_effect=OSError("Network down")),
    ):
        with pytest.raises(UpdateFailed) as excinfo:
            await coordinator._async_update_data()
        assert "connection error" in str(excinfo.value)
