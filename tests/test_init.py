"""Test initialization of Radio Thermostat integration."""

from unittest.mock import MagicMock, patch, AsyncMock
import pytest

import custom_components.radiotherm as radiotherm_init


class MockConfigEntry:
    def __init__(self, data=None, entry_id="test_entry"):
        self.data = data or {"host": "192.168.1.100"}
        self.entry_id = entry_id
        self.runtime_data = None
        self.update_listeners = []

    def async_on_unload(self, listener):
        self.update_listeners.append(listener)

    def add_update_listener(self, listener):
        self.update_listeners.append(listener)
        return lambda: self.update_listeners.remove(listener)


@pytest.fixture
def mock_hass():
    """Mock Home Assistant."""
    hass = MagicMock()
    hass.config_entries = MagicMock()

    async def forward_setups(*args, **kwargs):
        return True

    hass.config_entries.async_forward_entry_setups = AsyncMock(
        side_effect=forward_setups
    )
    hass.async_add_executor_job = AsyncMock(side_effect=lambda func, *args: func(*args))
    return hass


@pytest.mark.asyncio
async def test_async_setup_entry_no_hold(mock_hass):
    """Test async_setup_entry when hold is False."""
    entry = MockConfigEntry()

    # Mock init data
    mock_init_data = MagicMock()
    mock_init_data.name = "Living Room"
    mock_init_data.host = "192.168.1.100"
    mock_init_data.tstat = MagicMock()

    # Mock coordinator data
    mock_coordinator_data = MagicMock()
    mock_coordinator_data.tstat = {"hold": False}

    with (
        patch(
            "custom_components.radiotherm.async_get_init_data",
            AsyncMock(return_value=mock_init_data),
        ) as mock_get_init,
        patch(
            "custom_components.radiotherm.RadioThermUpdateCoordinator"
        ) as mock_coord_class,
        patch(
            "custom_components.radiotherm.async_set_time", AsyncMock()
        ) as mock_set_time,
    ):

        mock_coordinator = MagicMock()
        mock_coordinator.data = mock_coordinator_data
        mock_coordinator.async_config_entry_first_refresh = AsyncMock()
        mock_coord_class.return_value = mock_coordinator

        result = await radiotherm_init.async_setup_entry(mock_hass, entry)

        assert result is True
        assert entry.runtime_data == mock_coordinator
        mock_get_init.assert_called_once_with(mock_hass, "192.168.1.100")
        mock_coord_class.assert_called_once_with(mock_hass, entry, mock_init_data)
        mock_coordinator.async_config_entry_first_refresh.assert_called_once()
        mock_set_time.assert_called_once_with(mock_hass, mock_init_data.tstat)
        mock_hass.config_entries.async_forward_entry_setups.assert_called_once()


@pytest.mark.asyncio
async def test_async_setup_entry_with_hold(mock_hass):
    """Test async_setup_entry when hold is True (should not sync time)."""
    entry = MockConfigEntry()

    # Mock init data
    mock_init_data = MagicMock()
    mock_init_data.name = "Living Room"
    mock_init_data.host = "192.168.1.100"
    mock_init_data.tstat = MagicMock()

    # Mock coordinator data
    mock_coordinator_data = MagicMock()
    mock_coordinator_data.tstat = {"hold": True}

    with (
        patch(
            "custom_components.radiotherm.async_get_init_data",
            AsyncMock(return_value=mock_init_data),
        ),
        patch(
            "custom_components.radiotherm.RadioThermUpdateCoordinator"
        ) as mock_coord_class,
        patch(
            "custom_components.radiotherm.async_set_time", AsyncMock()
        ) as mock_set_time,
    ):

        mock_coordinator = MagicMock()
        mock_coordinator.data = mock_coordinator_data
        mock_coordinator.async_config_entry_first_refresh = AsyncMock()
        mock_coord_class.return_value = mock_coordinator

        result = await radiotherm_init.async_setup_entry(mock_hass, entry)

        assert result is True
        mock_set_time.assert_not_called()


@pytest.mark.asyncio
async def test_async_unload_entry(mock_hass):
    """Test unloading config entry."""
    entry = MockConfigEntry()

    async def unload_platforms(*args, **kwargs):
        return True

    mock_hass.config_entries.async_unload_platforms = AsyncMock(
        side_effect=unload_platforms
    )

    result = await radiotherm_init.async_unload_entry(mock_hass, entry)
    assert result is True
    mock_hass.config_entries.async_unload_platforms.assert_called_once_with(
        entry, radiotherm_init.PLATFORMS
    )
