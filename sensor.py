"""VirtualPoolCare sensor platform."""
import logging
from datetime import timedelta
import random

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN, SCAN_INTERVAL_HOURS

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform via YAML."""
    interval_hrs = config.get("update_interval_hours", SCAN_INTERVAL_HOURS)
    update_interval = timedelta(hours=interval_hrs)

    coordinator = VirtualPoolCareDataUpdateCoordinator(
        hass, name=DOMAIN, update_interval=update_interval
    )
    await coordinator.async_config_entry_first_refresh()

    entities = []
    if coordinator.data:
        for key in coordinator.data:
            entities.append(VirtualPoolCareSensor(coordinator, key))
    async_add_entities(entities, update_before_add=False)

    # Store entities for dynamic addition
    hass.data.setdefault(f"{DOMAIN}_entities", []).extend(entities)

    # Register a listener to add new entities dynamically if keys change
    coordinator.async_add_listener(
        lambda: _add_new_virtualpoolcare_entities(hass, coordinator, async_add_entities)
    )


def _add_new_virtualpoolcare_entities(hass, coordinator, async_add_entities):
    """Add entities if new keys appear in coordinator.data."""
    existing_keys = {
        ent._key for ent in hass.data.get(f"{DOMAIN}_entities", [])
    }
    new_keys = set(coordinator.data or {}) - existing_keys
    if new_keys:
        new_entities = [VirtualPoolCareSensor(coordinator, key) for key in new_keys]
        async_add_entities(new_entities, update_before_add=False)
        hass.data.setdefault(f"{DOMAIN}_entities", []).extend(new_entities)


class VirtualPoolCareDataUpdateCoordinator(DataUpdateCoordinator):
    """Manages fetching data from virtualpoolcare.io every X hours."""

    def __init__(self, hass: HomeAssistant, name: str, update_interval: timedelta):
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from virtualpoolcare.io (runs in executor)."""
        try:
            # Replace fetch_virtualpoolcare_data() with your actual function
            result = await self.hass.async_add_executor_job(fetch_virtualpoolcare_data)
            return result
        except Exception as err:
            raise UpdateFailed(f"Error fetching VirtualPoolCare data: {err}") from err


class VirtualPoolCareSensor(SensorEntity):
    """Representation of a single VirtualPoolCare sensor."""

    def __init__(self, coordinator: VirtualPoolCareDataUpdateCoordinator, key: str):
        self.coordinator = coordinator
        self._key = key
        self._attr_unique_id = f"{DOMAIN}_{key}"
        self._attr_name = f"{DOMAIN} {key}"

    @property
    def native_unit_of_measurement(self):
        """Return unit if applicable (e.g., "°F" or "ppm")."""
        return None

    @property
    def state(self):
        """Return the current state for this key."""
        if self.coordinator.data and self._key in self.coordinator.data:
            return self.coordinator.data[self._key]
        return None

    async def async_update(self):
        await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        """Register listener so HA updates state when coordinator data changes."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self._handle_coordinator_update)
        )

    @callback
    def _handle_coordinator_update(self):
        """Write updated state back to HA when coordinator data changes."""
        self.async_write_ha_state()


def fetch_virtualpoolcare_data() -> dict:
    """
    Replace this stub with your actual code that:
    1. Logs in (or uses an API key) to virtualpoolcare.io/BlueRiiot.
    2. Downloads JSON or CSV.
    3. Parses out a dict mapping unique sensor‐keys → values.
    Example return format:
        {
          "water_temperature": 78.2,
          "pH_level": 7.4,
          "chlorine_ppm": 1.2,
          "device_status": "online"
        }
    """
    # -------------- placeholder logic --------------
    # In reality, import requests, call the API, etc.
    return {
        "water_temperature": round(random.uniform(75.0, 85.0), 1),
        "pH_level": round(random.uniform(7.0, 8.0), 2),
        "chlorine_ppm": round(random.uniform(0.5, 3.0), 1),
    }