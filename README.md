# Financieel Beheer

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

A Home Assistant custom integration for **Financieel Beheer** (Finance Manager). This integration connects Home Assistant to the Financieel Beheer addon and provides a sensor that tracks the number of bank transactions requiring review.

## Features

- Sensor showing the number of transactions awaiting review
- Service to sync new transactions from all linked bank connections
- Configuration via the Home Assistant UI (config flow)

## Requirements

- Home Assistant 2024.1.0 or newer


## Installation

### Via HACS

1. Open HACS in Home Assistant.
2. Go to **Integrations** and click the three-dot menu in the top right.
3. Select **Custom repositories** and add:
   - Repository: `jralieve/ha-ApD04nYFJmuKpmIn`
   - Category: `Integration`
4. Click **Add**, then find **Financieel Beheer** in the list and install it.
5. Restart Home Assistant.

### Manual

1. Copy the `custom_components/ha_finance` directory into your Home Assistant `custom_components` folder.
2. Restart Home Assistant.

## Configuration

1. Go to **Settings → Devices & Services** and click **Add Integration**.
2. Search for **Financieel Beheer**.
3. Enter the URL of your Financieel Beheer addon and the API token.

## Services

| Service | Description |
|---------|-------------|
| `ha_finance.sync_transactions` | Fetches new transactions from all linked bank connections. |

## Support

- [Issue tracker](https://github.com/jralieve/ha-finance-addon/issues)
- [Documentation](https://github.com/jralieve/ha-finance-addon)
