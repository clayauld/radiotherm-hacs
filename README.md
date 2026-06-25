# Radio Thermostat Custom Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Test Suite](https://github.com/clayauld/radiotherm-hacs/actions/workflows/test.yml/badge.svg)](https://github.com/clayauld/radiotherm-hacs/actions/workflows/test.yml)

A replacement for the official Radio Thermostat integration. It works with wifi-enabled Radio Thermostat devices (Filtrete 3M50, CT30, CT50, CT80, CT80 Plus, etc.) in Home Assistant. This is a local polling integration that maintains support for modern Home Assistant Climate architectures (specifically addressing the required `TURN_ON` and `TURN_OFF` features in Core 2024.2+).

## Features

- **Climate Entity:** Control target temperature, operation modes (heat, cool, auto, off), and fan modes (on, auto, circulate).
- **Hold Switch:** Toggle permanent hold on/off.
- **Local Control:** Communicates directly with the thermostat's API over your local network.
- **Time Synchronization:** Automatically syncs the thermostat's clock every 24 hours. This behavior can be toggled on/off in the integration options, or manually triggered at any time using the `climate.sync_time` service.
- **Modern Compatibility:** Native support for the modern `ClimateEntityFeature` bitmasks.

## Versatile Thermostat Compatibility

This integration includes a built-in runtime patch for the **Versatile Thermostat** custom integration. When this integration loads, it dynamically monkey-patches `versatile_thermostat`'s underlying climate handler to cast the `supported_features` attribute to `ClimateEntityFeature`. This resolves the `TypeError: argument of type 'int' is not a container or iterable` crash that occurs when adjusting target temperatures of `over_climate` devices in Versatile Thermostat.

## Installation

### Method 1: HACS (Recommended)

1. Open **HACS** in your Home Assistant interface.
2. Click the three dots in the top-right corner and select **Custom repositories**.
3. Enter the URL of this repository and select **Integration** as the category.
4. Click **Add**, then search for and install **Radio Thermostat**.
5. Restart Home Assistant.

### Method 2: Manual Installation

1. Copy the `custom_components/radiotherm` directory to your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.

## Configuration

The integration is configured via the Home Assistant user interface:
1. Go to **Settings -> Devices & Services**.
2. Click **Add Integration** in the bottom-right.
3. Search for **Radio Thermostat** and enter your thermostat's IP address.
4. **Options Flow**: You can configure Options by clicking **Configure** on the integration card to toggle the automatic time synchronization behavior.

## Development

### Setup Dev Environment
This project uses [uv](https://github.com/astral-sh/uv) to manage its virtual environment and dependencies. To set up the virtual environment:
```bash
make venv
```

### Running Tests
To run the test suite:
```bash
make test
```

### Running Formatters and Linters
To automatically format the code:
```bash
make format
```

To run linting checks (flake8, black, isort, mypy, bandit):
```bash
make lint
```
