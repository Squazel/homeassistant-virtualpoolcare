# VirtualPoolCare Integration

Fetches your pool's water‐chemistry, device status, and usage metrics from VirtualPoolCare.io (Blue Riiot) and exposes them as Home Assistant sensors.

## Features

- Retrieves water temperature, pH, chlorine levels, etc.
- Updates on a configurable interval (default: 6 hours).
- Each metric becomes its own `sensor.virtualpoolcare_<metric>` entity.

## Installation via HACS

**1.** Ensure [HACS](https://hacs.xyz/) is installed.  
**2.** Go to **HACS → Integrations → ••• (top-right) → Custom Repositories**.  
**3.** Add:
```
https://github.com/YourUsername/homeassistant-virtualpoolcare
```
**Category:** Integration  
**4.** Go back to **HACS → Integrations**, find "VirtualPoolCare Integration," click **Install**.  
**5.** Restart Home Assistant.

## Manual Installation

**1.** Clone into your HA `custom_components/` directory:
```bash
cd /config/custom_components
git clone https://github.com/YourUsername/homeassistant-virtualpoolcare.git
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

## Configuration Options

| Option | Type | Default | Required | Description |
|--------|------|---------|----------|-------------|
| email | string | - | **Yes** | Your VirtualPoolCare.io login email |
| password | string | - | **Yes** | Your VirtualPoolCare.io login password |
| update_interval_hours | number | 6 | No | How often (in hours) to fetch data from VirtualPoolCare |

## Security Note

⚠️ **Important**: Your VirtualPoolCare credentials will be stored in your `configuration.yaml` file. Make sure this file is properly secured and not accessible to unauthorized users.

## Changelog & Releases

See [Releases](https://github.com/YourUsername/homeassistant-virtualpoolcare/releases) for version history.

## License

Licensed under the MIT License. See [LICENSE](LICENSE) for details.