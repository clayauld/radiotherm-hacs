"""Test Radio Thermostat config flow."""

from unittest.mock import MagicMock, AsyncMock, patch
import pytest

from custom_components.radiotherm.config_flow import (
    RadioThermConfigFlow,
    CannotConnect,
)


# Define FlowResultType locally
class FlowResultType:
    FORM = "form"
    CREATE_ENTRY = "create_entry"
    ABORT = "abort"


@pytest.fixture
def mock_hass():
    """Mock Home Assistant."""
    hass = MagicMock()
    hass.async_add_executor_job = AsyncMock(side_effect=lambda func, *args: func(*args))
    return hass


@pytest.mark.asyncio
async def test_step_user_init(mock_hass):
    """Test user step initial form."""
    flow = RadioThermConfigFlow()
    flow.hass = mock_hass

    result = await flow.async_step_user()
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}


@pytest.mark.asyncio
async def test_step_user_success(mock_hass):
    """Test user step with valid input."""
    flow = RadioThermConfigFlow()
    flow.hass = mock_hass

    mock_init_data = MagicMock()
    mock_init_data.name = "Living Room"
    mock_init_data.mac = "00:11:22:33:44:55"
    mock_init_data.host = "192.168.1.100"

    user_input = {"host": "192.168.1.100"}

    with patch(
        "custom_components.radiotherm.config_flow.validate_connection",
        AsyncMock(return_value=mock_init_data),
    ) as mock_validate:

        result = await flow.async_step_user(user_input)

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == "Living Room"
        assert result["data"] == user_input
        mock_validate.assert_called_once_with(mock_hass, "192.168.1.100")


@pytest.mark.asyncio
async def test_step_user_cannot_connect(mock_hass):
    """Test user step failing to connect."""
    flow = RadioThermConfigFlow()
    flow.hass = mock_hass

    user_input = {"host": "192.168.1.100"}

    with patch(
        "custom_components.radiotherm.config_flow.validate_connection",
        AsyncMock(side_effect=CannotConnect("Connection failed")),
    ):
        result = await flow.async_step_user(user_input)

        assert result["type"] == FlowResultType.FORM
        assert result["errors"] == {"host": "cannot_connect"}


@pytest.mark.asyncio
async def test_step_user_unexpected_exception(mock_hass):
    """Test user step with an unexpected exception."""
    flow = RadioThermConfigFlow()
    flow.hass = mock_hass

    user_input = {"host": "192.168.1.100"}

    with patch(
        "custom_components.radiotherm.config_flow.validate_connection",
        AsyncMock(side_effect=Exception("Unexpected")),
    ):
        result = await flow.async_step_user(user_input)

        assert result["type"] == FlowResultType.FORM
        assert result["errors"] == {"base": "unknown"}


@pytest.mark.asyncio
async def test_step_dhcp_success(mock_hass):
    """Test dhcp discovery flow."""
    flow = RadioThermConfigFlow()
    flow.hass = mock_hass

    discovery_info = MagicMock()
    discovery_info.ip = "192.168.1.101"

    mock_init_data = MagicMock()
    mock_init_data.name = "Living Room"
    mock_init_data.mac = "00:11:22:33:44:55"
    mock_init_data.host = "192.168.1.101"
    mock_init_data.model = "CT80"

    with patch(
        "custom_components.radiotherm.config_flow.validate_connection",
        AsyncMock(return_value=mock_init_data),
    ):
        result = await flow.async_step_dhcp(discovery_info)

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "confirm"
        assert flow.discovered_ip == "192.168.1.101"
        assert flow.discovered_init_data == mock_init_data


@pytest.mark.asyncio
async def test_step_dhcp_cannot_connect(mock_hass):
    """Test dhcp discovery flow failure."""
    flow = RadioThermConfigFlow()
    flow.hass = mock_hass

    discovery_info = MagicMock()
    discovery_info.ip = "192.168.1.101"

    with patch(
        "custom_components.radiotherm.config_flow.validate_connection",
        AsyncMock(side_effect=CannotConnect),
    ):
        result = await flow.async_step_dhcp(discovery_info)

        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "cannot_connect"


@pytest.mark.asyncio
async def test_step_confirm(mock_hass):
    """Test confirmation step in discovery."""
    flow = RadioThermConfigFlow()
    flow.hass = mock_hass

    mock_init_data = MagicMock()
    mock_init_data.name = "Living Room"
    mock_init_data.host = "192.168.1.101"
    mock_init_data.model = "CT80"

    flow.discovered_ip = "192.168.1.101"
    flow.discovered_init_data = mock_init_data

    # Check form rendering
    result = await flow.async_step_confirm()
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "confirm"

    # Check submission
    result = await flow.async_step_confirm(user_input={})
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Living Room"
    assert result["data"] == {"host": "192.168.1.101"}


@pytest.mark.asyncio
async def test_options_flow(mock_hass):
    """Test options flow."""
    entry = MagicMock()
    entry.options = {"sync_time": False}

    from custom_components.radiotherm.config_flow import RadioThermOptionsFlowHandler

    handler = RadioThermOptionsFlowHandler(entry)
    handler.hass = mock_hass
    handler.async_show_form = MagicMock(
        return_value={"type": FlowResultType.FORM, "step_id": "init"}
    )
    handler.async_create_entry = MagicMock(
        side_effect=lambda title, data: {
            "type": FlowResultType.CREATE_ENTRY,
            "data": data,
        }
    )

    # Initial step
    result = await handler.async_step_init()
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    # Submit options
    result = await handler.async_step_init(user_input={"sync_time": True})
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"] == {"sync_time": True}
