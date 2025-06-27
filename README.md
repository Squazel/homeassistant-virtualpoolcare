# VirtualPoolCare Integration

Fetches your pool's water‐chemistry, device status, and usage metrics from VirtualPoolCare.io (Blue Riiot) and exposes them as Home Assistant sensors.

TODO: Add a blurb here about why this is better/easier than trying to get the data directly from the Blue Connect, and also how to go about setting up an account.

## Features

- Retrieves water temperature, pH, chlorine levels, etc.
- Updates on a configurable interval (default: 6 hours).
- Each metric becomes its own `sensor.virtualpoolcare_<device_serial>_<metric>` entity.
- Sensors are grouped by device for easy organization.
- **Manual refresh supported:** Use the `virtualpoolcare.force_update` Home Assistant service to fetch new data on demand.

## Installation via HACS

**1.** Ensure [HACS](https://hacs.xyz/) is installed.  
**2.** Go to **HACS → Integrations → ••• (top-right) → Custom Repositories**.  
**3.** Add:
```
https://github.com/Squazel/homeassistant-virtualpoolcare
```
**Category:** Integration  
**4.** Go back to **HACS → Integrations**, find "VirtualPoolCare Integration," click **Install**.  
**5.** Restart Home Assistant.

## Manual Installation

**1.** Clone into your HA `custom_components/` directory:
```bash
cd /config/custom_components
git clone https://github.com/Squazel/homeassistant-virtualpoolcare.git homeassistant-virtualpoolcare
```
**2.** Restart Home Assistant.

## Configuration

Add the following to your `configuration.yaml`:

```yaml
sensor:
  - platform: virtualpoolcare
    email: "your_email@example.com"       # Required: Your VirtualPoolCare login email
    password: "your_password"             # Required: Your VirtualPoolCare password
    update_interval_hours: 4              # Optional: How often to fetch data (default: 6 hours)
```

**3.** Restart Home Assistant again.

## Example Entities

After configuration, you'll get sensors like:
- `sensor.virtualpoolcare_0A2B3C4D_temperature`
- `sensor.virtualpoolcare_0A2B3C4D_ph` 
- `sensor.virtualpoolcare_0A2B3C4D_orp`
- `sensor.virtualpoolcare_0A2B3C4D_salinity`

Where `0A2B3C4D` is your Blue Riiot device serial number.

## Configuration Options

| Option | Type | Default | Required | Description |
|--------|------|---------|----------|-------------|
| email | string | - | **Yes** | Your VirtualPoolCare.io login email |
| password | string | - | **Yes** | Your VirtualPoolCare.io login password |
| update_interval_hours | number | 6 | No | How often (in hours) to fetch data from VirtualPoolCare |

## Security Note

⚠️ **Important**: Your VirtualPoolCare credentials will be stored in your `configuration.yaml` file. Make sure this file is properly secured and not accessible to unauthorized users.

## Development & Testing

For developers who want to contribute or test locally without Home Assistant:

📋 **[See Testing Guide](tests/README.md)** - Complete guide for setting up and running the test harness locally.

Key testing features:
- 🧪 **Unit tests** with pytest
- 🔧 **Development test suite** for debugging
- 🎯 **Standalone test runner** for quick verification
- 🏠 **No Home Assistant required** for testing

## Contributing

Found a bug or want to contribute? Please:

1. **Report issues**: Use [GitHub Issues](https://github.com/Squazel/homeassistant-virtualpoolcare/issues)
2. **Submit pull requests**: Use [GitHub Pull Requests](https://github.com/Squazel/homeassistant-virtualpoolcare/pulls)
3. **Read the testing guide**: [tests/README.md](tests/README.md)

## Changelog & Releases

See [Releases](https://github.com/Squazel/homeassistant-virtualpoolcare/releases) for version history.

## License

Licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Manual Refresh

If you want to fetch new data immediately (outside the normal polling interval), you can call the `virtualpoolcare.force_update` service from the Home Assistant UI or in automations/scripts:

**From Developer Tools → Services:**
- Select `virtualpoolcare.force_update` and click "Call Service".

**From YAML:**
```yaml
service: virtualpoolcare.force_update
```

This will trigger an immediate update from VirtualPoolCare.