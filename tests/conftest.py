"""Pytest configuration and mocks for Radio Thermostat tests."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add the custom_components directory to the Python path
project_root = Path(__file__).parent.parent
custom_components_path = project_root / "custom_components"
sys.path.insert(0, str(custom_components_path))

# Add the radiotherm component directory to the Python path
radiotherm_component_path = custom_components_path / "radiotherm"
sys.path.insert(0, str(radiotherm_component_path))

# Create mocked modules
homeassistant = MagicMock()
components = MagicMock()
helpers = MagicMock()
service_info = MagicMock()
dhcp = MagicMock()
const = MagicMock()
util = MagicMock()
dt = MagicMock()
config_entries = MagicMock()
exceptions = MagicMock()
entity_platform = MagicMock()
device_registry = MagicMock()
update_coordinator = MagicMock()
climate = MagicMock()
switch = MagicMock()
core = MagicMock()

# Link attributes to match import paths traversing parent attributes
homeassistant.components = components
homeassistant.helpers = helpers
homeassistant.const = const
homeassistant.util = util
homeassistant.config_entries = config_entries
homeassistant.exceptions = exceptions
homeassistant.core = core

components.climate = climate
components.switch = switch

helpers.entity_platform = entity_platform
helpers.device_registry = device_registry
helpers.update_coordinator = update_coordinator
helpers.service_info = service_info
service_info.dhcp = dhcp

util.dt = dt

# Set them in sys.modules
sys.modules["homeassistant"] = homeassistant
sys.modules["homeassistant.components"] = components
sys.modules["homeassistant.components.climate"] = climate
sys.modules["homeassistant.components.switch"] = switch
sys.modules["homeassistant.config_entries"] = config_entries
sys.modules["homeassistant.core"] = core
sys.modules["homeassistant.exceptions"] = exceptions
sys.modules["homeassistant.helpers"] = helpers
sys.modules["homeassistant.helpers.entity_platform"] = entity_platform
sys.modules["homeassistant.helpers.device_registry"] = device_registry
sys.modules["homeassistant.helpers.update_coordinator"] = update_coordinator
sys.modules["homeassistant.helpers.service_info"] = service_info
sys.modules["homeassistant.helpers.service_info.dhcp"] = dhcp
sys.modules["homeassistant.const"] = const
sys.modules["homeassistant.util"] = util
sys.modules["homeassistant.util.dt"] = dt
sys.modules["voluptuous"] = MagicMock()

# Real identity function for callback decorator
core.callback = lambda x: x

# Mock third-party radiotherm modules
radiotherm_mock = MagicMock()
radiotherm_validate = MagicMock()
radiotherm_thermostat = MagicMock()

# Link attributes for radiotherm mock to resolve nested references
radiotherm_mock.thermostat = radiotherm_thermostat
radiotherm_mock.validate = radiotherm_validate

sys.modules["radiotherm"] = radiotherm_mock
sys.modules["radiotherm.validate"] = radiotherm_validate
sys.modules["radiotherm.thermostat"] = radiotherm_thermostat


# Real exception class for RadiothermTstatError
class MockRadiothermTstatError(Exception):
    pass


radiotherm_validate.RadiothermTstatError = MockRadiothermTstatError


# Real classes for CT80, CT30, and CommonThermostat to
# support isinstance() checks and spec'ing
class CT80:
    pass


class CT30:
    pass


class CommonThermostat:
    pass


radiotherm_thermostat.CT80 = CT80
radiotherm_thermostat.CT30 = CT30
radiotherm_thermostat.CommonThermostat = CommonThermostat

# Mock specific imports and structures used inside the component
const.CONF_HOST = "host"
const.Platform = MagicMock()
const.Platform.CLIMATE = "climate"
const.Platform.SWITCH = "switch"
const.ATTR_TEMPERATURE = "temperature"
const.PRECISION_HALVES = 0.5
const.UnitOfTemperature = MagicMock()
const.UnitOfTemperature.FAHRENHEIT = "F"


class ClimateEntityFeature:
    TARGET_TEMPERATURE = 1
    FAN_MODE = 2
    PRESET_MODE = 16
    TURN_OFF = 128
    TURN_ON = 256


climate.ClimateEntityFeature = ClimateEntityFeature
climate.FAN_AUTO = "auto"
climate.FAN_OFF = "off"
climate.FAN_ON = "on"
climate.PRESET_AWAY = "away"
climate.PRESET_HOME = "home"
climate.HVACAction = MagicMock()
climate.HVACAction.IDLE = "idle"
climate.HVACAction.HEATING = "heating"
climate.HVACAction.COOLING = "cooling"
climate.HVACMode = MagicMock()
climate.HVACMode.AUTO = "auto"
climate.HVACMode.COOL = "cool"
climate.HVACMode.HEAT = "heat"
climate.HVACMode.OFF = "off"

# Mock HomeAssistantError to support try-except catching
exceptions.HomeAssistantError = Exception

device_registry.format_mac = lambda uuid: uuid
device_registry.CONNECTION_NETWORK_MAC = "mac"


class MockDataUpdateCoordinator:
    def __init__(self, hass, logger, **kwargs):
        self.hass = hass
        self.logger = logger
        self.name = kwargs.get("name")
        self.update_interval = kwargs.get("update_interval")
        self.data = None
        self.config_entry = kwargs.get("config_entry")

    async def async_config_entry_first_refresh(self):
        pass

    async def async_request_refresh(self):
        pass

    def __class_getitem__(cls, item):
        return cls


update_coordinator.DataUpdateCoordinator = MockDataUpdateCoordinator
update_coordinator.UpdateFailed = Exception


# Mock base classes with property getters delegating to _attr_* fields
class MockEntity:
    @property
    def unique_id(self):
        return getattr(self, "_attr_unique_id", None)

    @property
    def name(self):
        return getattr(self, "_attr_name", None)

    @property
    def supported_features(self):
        return getattr(self, "_attr_supported_features", None)

    @property
    def device_info(self):
        return getattr(self, "_attr_device_info", None)


class MockClimateEntity(MockEntity):
    @property
    def fan_modes(self):
        return getattr(self, "_attr_fan_modes", None)

    @property
    def fan_mode(self):
        return getattr(self, "_attr_fan_mode", None)

    @property
    def preset_modes(self):
        return getattr(self, "_attr_preset_modes", None)

    @property
    def preset_mode(self):
        return getattr(self, "_attr_preset_mode", None)

    @property
    def hvac_modes(self):
        return getattr(self, "_attr_hvac_modes", None)

    @property
    def hvac_mode(self):
        return getattr(self, "_attr_hvac_mode", None)

    @property
    def hvac_action(self):
        return getattr(self, "_attr_hvac_action", None)

    @property
    def target_temperature(self):
        return getattr(self, "_attr_target_temperature", None)

    @property
    def current_temperature(self):
        return getattr(self, "_attr_current_temperature", None)


class MockSwitchEntity(MockEntity):
    @property
    def is_on(self):
        return getattr(self, "_attr_is_on", None)

    @property
    def translation_key(self):
        return getattr(self, "_attr_translation_key", None)


climate.ClimateEntity = MockClimateEntity
switch.SwitchEntity = MockSwitchEntity


class MockCoordinatorEntity(MockEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.hass = coordinator.hass

    def async_write_ha_state(self):
        pass

    def __class_getitem__(cls, item):
        return cls


update_coordinator.CoordinatorEntity = MockCoordinatorEntity


class MockConfigFlow:
    def __init__(self, *args, **kwargs):
        pass

    def __init_subclass__(cls, **kwargs):
        pass

    @property
    def hass(self):
        if not hasattr(self, "_hass"):
            self._hass = MagicMock()
        return self._hass

    @hass.setter
    def hass(self, value):
        self._hass = value

    @property
    def context(self):
        if not hasattr(self, "_context"):
            self._context = {}
        return self._context

    @context.setter
    def context(self, value):
        self._context = value

    @property
    def unique_id(self):
        if not hasattr(self, "_unique_id"):
            self._unique_id = None
        return self._unique_id

    @unique_id.setter
    def unique_id(self, value):
        self._unique_id = value

    async def async_set_unique_id(self, unique_id, raise_on_progress=True):
        self.unique_id = unique_id
        return unique_id

    def _abort_if_unique_id_configured(self, updates=None, reload_on_update=True):
        pass

    def _async_abort_entries_match(self, match_dict):
        pass

    def async_abort(self, reason):
        return {"type": "abort", "reason": reason}

    def _set_confirm_only(self):
        pass

    def async_show_form(
        self, step_id, data_schema=None, errors=None, description_placeholders=None
    ):
        return {
            "type": "form",
            "step_id": step_id,
            "errors": errors or {},
            "description_placeholders": description_placeholders or {},
        }

    def async_create_entry(
        self,
        title,
        data,
        description=None,
        description_placeholders=None,
        options=None,
    ):
        return {
            "type": "create_entry",
            "title": title,
            "data": data,
            "options": options,
        }


class MockOptionsFlow:
    def __init__(self, config_entry=None, *args, **kwargs):
        self.config_entry = config_entry

    def __init_subclass__(cls, **kwargs):
        pass

    def async_show_form(
        self, step_id, data_schema=None, errors=None, description_placeholders=None
    ):
        return {
            "type": "form",
            "step_id": step_id,
            "errors": errors or {},
            "description_placeholders": description_placeholders or {},
        }

    def async_create_entry(
        self,
        title,
        data,
        description=None,
        description_placeholders=None,
        options=None,
    ):
        return {
            "type": "create_entry",
            "title": title,
            "data": data,
            "options": options,
        }


config_entries.ConfigFlow = MockConfigFlow
config_entries.OptionsFlow = MockOptionsFlow
