"""VirtualPoolCare sensor platform."""
import logging
from datetime import timedelta, datetime

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import dt as dt_util
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, SCAN_INTERVAL_HOURS
from .virtualpoolcare_core import VirtualPoolCareAPI, VirtualPoolCareSensorData

_LOGGER = logging.getLogger(__name__)

# TODO: Implement config flow for UI wizard setup
# This would involve:
# 1. Creating config_flow.py with user input forms
# 2. Adding strings.json for UI text
# 3. Adding translations for multiple languages
# 4. Moving from YAML configuration to config entries
# This would make the integration appear in the Integrations UI as a first-class citizen

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up VirtualPoolCare sensors from config entry."""
    # Get the coordinator that was created in __init__.py
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # No need to call any refresh methods - coordinator already has data
    # from async_config_entry_first_refresh() called in __init__.py
    
    entities = []
    if coordinator.data:
        sensor_keys = VirtualPoolCareSensorData.get_sensor_keys(coordinator.data)
        for key in sensor_keys:
            entities.append(VirtualPoolCareSensor(coordinator, key))
    
    async_add_entities(entities, update_before_add=False)

# Keep existing async_setup_platform for YAML compatibility
async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform via YAML."""
    _LOGGER.info("VirtualPoolCare: Starting platform setup")
    
    # Get configuration values
    email = config.get("email")
    password = config.get("password")
    interval_hrs = config.get("update_interval_hours", SCAN_INTERVAL_HOURS)
    
    _LOGGER.info("VirtualPoolCare: Config - email: %s, interval_hrs: %s", email[:5] + "***" if email else None, interval_hrs)
    
    # Validate required configuration
    if not email or not password:
        _LOGGER.error("VirtualPoolCare: email and password are required in configuration")
        return
    
    update_interval = timedelta(hours=interval_hrs)

    coordinator = VirtualPoolCareDataUpdateCoordinator(
        hass, 
        name=DOMAIN, 
        update_interval=update_interval,
        email=email,
        password=password
    )
    
    # For YAML setup, use async_request_refresh instead
    await coordinator.async_request_refresh()
    
    _LOGGER.info("VirtualPoolCare: First refresh completed. Data available: %s", bool(coordinator.data))
    if coordinator.data:
        _LOGGER.debug("VirtualPoolCare: Data keys: %s", list(coordinator.data.keys()))

    entities = []
    if coordinator.data:
        sensor_keys = VirtualPoolCareSensorData.get_sensor_keys(coordinator.data)
        _LOGGER.info("VirtualPoolCare: Found %d sensor keys: %s", len(sensor_keys), sensor_keys)
        
        for key in sensor_keys:
            entities.append(VirtualPoolCareSensor(coordinator, key))
    else:
        _LOGGER.warning("VirtualPoolCare: No data received from coordinator")
    
    _LOGGER.info("VirtualPoolCare: Adding %d entities to Home Assistant", len(entities))
    async_add_entities(entities, update_before_add=False)

    # Store entities for dynamic addition
    hass.data.setdefault(f"{DOMAIN}_entities", []).extend(entities)

    # Register a listener to add new entities dynamically if keys change
    coordinator.async_add_listener(
        lambda: _add_new_virtualpoolcare_entities(hass, coordinator, async_add_entities)
    )


def _add_new_virtualpoolcare_entities(hass, coordinator, async_add_entities):
    """Add entities if new keys appear in coordinator.data."""
    device_serial = coordinator.data.get("blue_device_serial", "unknown")
    
    existing_keys = {
        ent._key for ent in hass.data.get(f"{DOMAIN}_entities", [])
        if hasattr(ent, '_device_serial') and ent._device_serial == device_serial
    }
    
    sensor_keys = VirtualPoolCareSensorData.get_sensor_keys(coordinator.data)
    new_keys = sensor_keys - existing_keys
    
    if new_keys:
        new_entities = [VirtualPoolCareSensor(coordinator, key) for key in new_keys]
        async_add_entities(new_entities, update_before_add=False)
        hass.data.setdefault(f"{DOMAIN}_entities", []).extend(new_entities)


class VirtualPoolCareDataUpdateCoordinator(DataUpdateCoordinator):
    """Manages fetching data from virtualpoolcare.io every X hours."""

    def __init__(self, hass: HomeAssistant, name: str, update_interval: timedelta, email: str, password: str):
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=update_interval,
        )
        self.api = VirtualPoolCareAPI(email, password)

    async def _async_update_data(self) -> dict:
        """Fetch data from virtualpoolcare.io (runs in executor)."""
        try:
            result = await self.hass.async_add_executor_job(self.api.fetch_data)
            return result
        except Exception as err:
            raise UpdateFailed(f"Error fetching VirtualPoolCare data: {err}") from err


class VirtualPoolCareSensor(SensorEntity):
    """Representation of a single VirtualPoolCare sensor."""

    def __init__(self, coordinator: VirtualPoolCareDataUpdateCoordinator, key: str):
        self.coordinator = coordinator
        self._key = key
        
        # Get device serial from coordinator data for unique identification
        device_serial = coordinator.data.get("blue_device_serial", "unknown")
        
        # Use core module to create IDs and names
        self._attr_unique_id = VirtualPoolCareSensorData.create_entity_id(device_serial, key)
        self._attr_name = VirtualPoolCareSensorData.create_entity_name(device_serial, key)
        
        # Store device serial for use in device_info
        self._device_serial = device_serial
        
        # Set state class for historical data
        if key in ["temperature", "ph", "orp", "salinity", "chlorine_ppm", "chlorine", "tds", "conductivity"]:
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def extra_state_attributes(self):
        """Return additional state attributes."""
        attributes = {}
        
        # Add timestamp if available (also as attribute for compatibility)
        timestamp_key = f"{self._key}_timestamp"
        if self.coordinator.data and timestamp_key in self.coordinator.data:
            attributes["timestamp"] = self.coordinator.data[timestamp_key]
            
            # Also add human-readable timestamp
            try:
                dt = dt_util.parse_datetime(self.coordinator.data[timestamp_key])
                if dt:
                    attributes["last_measurement"] = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
            except (ValueError, TypeError):
                pass
        
        # Add expired status if available
        expired_key = f"{self._key}_expired"
        if self.coordinator.data and expired_key in self.coordinator.data:
            attributes["expired"] = self.coordinator.data[expired_key]
        
        # Add trend if available
        trend_key = f"{self._key}_trend"
        if self.coordinator.data and trend_key in self.coordinator.data:
            attributes["trend"] = self.coordinator.data[trend_key]
        
        # Add gauge and threshold data for the frontend card
        for attr in ['gauge_min', 'gauge_max', 'ok_min', 'ok_max', 'warning_low', 'warning_high', 'priority']:
            attr_key = f"{self._key}_{attr}"
            if self.coordinator.data and attr_key in self.coordinator.data:
                attributes[attr] = self.coordinator.data[attr_key]
        
        # Add device serial
        attributes["device_serial"] = self._device_serial
        
        # Add data freshness info based on actual measurement time
        measurement_time = self.last_updated
        if measurement_time:
            now = dt_util.utcnow()
            age_seconds = (now - measurement_time).total_seconds()
            age_hours = age_seconds / 3600
            attributes["data_age_hours"] = round(age_hours, 1)
            
            if age_hours > 24:
                attributes["data_freshness"] = "stale"
            elif age_hours > 12:
                attributes["data_freshness"] = "old"
            else:
                attributes["data_freshness"] = "fresh"
        
        return attributes

    @property
    def device_info(self):
        """Return device information for this sensor."""
        # Enhanced device info with API metadata
        device_info = {
            "identifiers": {(DOMAIN, self._device_serial)},
            "name": f"VirtualPoolCare Pool Monitor ({self._device_serial})",
            "manufacturer": "Blue Riiot",
            "model": "Pool Monitor",
            "sw_version": "1.0",
            "suggested_area": "Pool",
        }
        
        # Add dynamic metadata from API if available
        if self.coordinator.data:
            # Pool location/name if available
            pool_name = self.coordinator.data.get("pool_name")
            pool_location = self.coordinator.data.get("pool_location") 
            if pool_name:
                device_info["name"] = f"VirtualPoolCare {pool_name}"
            if pool_location:
                device_info["suggested_area"] = pool_location
            
            # Device firmware if available
            firmware_version = self.coordinator.data.get("firmware_version")
            if firmware_version:
                device_info["sw_version"] = firmware_version
                
            # Installation date if available
            install_date = self.coordinator.data.get("installation_date")
            if install_date:
                device_info["configuration_url"] = "https://app.virtualpoolcare.io"
                
        return device_info

    @property
    def native_unit_of_measurement(self):
        """Return unit if applicable."""
        return VirtualPoolCareSensorData.get_unit_of_measurement(self._key)

    @property
    def state(self):
        """Return the current state for this key."""
        if self.coordinator.data and self._key in self.coordinator.data:
            return self.coordinator.data[self._key]
        return None

    @property
    def last_updated(self):
        """Return when this sensor was last updated using API timestamp."""
        if not self.coordinator.data:
            return None
            
        timestamp_key = f"{self._key}_timestamp"
        if timestamp_key in self.coordinator.data:
            timestamp_str = self.coordinator.data[timestamp_key]
            try:
                # Parse ISO timestamp from VirtualPoolCare API
                return dt_util.parse_datetime(timestamp_str)
            except (ValueError, TypeError) as e:
                _LOGGER.warning("Could not parse timestamp %s for %s: %s", timestamp_str, self._key, e)
                return None
        return None

    async def async_update(self):
        """Request fresh data from the coordinator."""
        # Use async_refresh() instead of async_request_refresh() 
        # for manual updates to ensure data is fetched
        await self.coordinator.async_refresh()

    async def async_added_to_hass(self):
        """Register listener so HA updates state when coordinator data changes."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self._handle_coordinator_update)
        )

    @callback
    def _handle_coordinator_update(self):
        """Write updated state back to HA when coordinator data changes."""
        # For timestamp accuracy, we could try setting state with custom timestamp
        # but HA's recorder will still use the write time
        self.async_write_ha_state()
        
        # Log the actual vs desired timestamp for debugging
        if self.coordinator.data:
            timestamp_key = f"{self._key}_timestamp"
            if timestamp_key in self.coordinator.data:
                api_time = self.coordinator.data[timestamp_key]
                _LOGGER.debug("Entity %s: API timestamp %s, HA will record at %s", 
                            self._attr_name, api_time, dt_util.utcnow().isoformat())