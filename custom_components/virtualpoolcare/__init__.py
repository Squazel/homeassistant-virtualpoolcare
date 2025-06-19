"""The VirtualPoolCare integration."""
from __future__ import annotations

import logging
from pathlib import Path
from datetime import timedelta

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SCAN_INTERVAL_HOURS
from .sensor import VirtualPoolCareSensor, VirtualPoolCareSensorData, VirtualPoolCareDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

# Support both YAML and UI configuration
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema({
            vol.Required("email"): cv.string,
            vol.Required("password"): cv.string,
            vol.Optional("update_interval_hours", default=6): cv.positive_int,
        })
    }, 
    extra=vol.ALLOW_EXTRA
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the VirtualPoolCare component."""
    # Register the frontend card
    await _async_register_frontend_card(hass)
    
    # Handle YAML configuration
    if DOMAIN in config:
        # Set up platform via YAML (will call async_setup_platform in sensor.py)
        from homeassistant.helpers import discovery
        hass.async_create_task(
            discovery.async_load_platform(hass, "sensor", DOMAIN, config[DOMAIN], config)
        )
    
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up VirtualPoolCare sensors from config entry."""
    email = entry.data["email"]
    password = entry.data["password"]
    interval_hrs = entry.data.get("update_interval_hours", SCAN_INTERVAL_HOURS)
    
    update_interval = timedelta(hours=interval_hrs)

    coordinator = VirtualPoolCareDataUpdateCoordinator(
        hass, 
        name=DOMAIN, 
        update_interval=update_interval,
        email=email,
        password=password
    )
    
    # Use async_config_entry_first_refresh for initial setup
    await coordinator.async_config_entry_first_refresh()
    
    entities = []
    if coordinator.data:
        sensor_keys = VirtualPoolCareSensorData.get_sensor_keys(coordinator.data)
        for key in sensor_keys:
            entities.append(VirtualPoolCareSensor(coordinator, key))
    
    async_add_entities(entities, update_before_add=False)


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
    
    # For YAML setup, we should handle first refresh errors gracefully
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error("VirtualPoolCare: Failed to fetch initial data: %s", err)
        # Still create entities even if first fetch fails
        # The coordinator will retry on its normal schedule
    
    entities = []
    if coordinator.data:
        sensor_keys = VirtualPoolCareSensorData.get_sensor_keys(coordinator.data)
        for key in sensor_keys:
            entities.append(VirtualPoolCareSensor(coordinator, key))
    
    async_add_entities(entities, update_before_add=False)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_register_frontend_card(hass: HomeAssistant) -> None:
    """Register the frontend card."""
    try:
        # Get the path to our frontend file
        frontend_path = Path(__file__).parent / "frontend"
        card_file = frontend_path / "pool-readings-bar-card.js"
        
        if card_file.exists():
            # Register the static path for our frontend files using the new async method
            await hass.http.async_register_static_paths([
                StaticPathConfig(
                    f"/{DOMAIN}", 
                    str(frontend_path), 
                    cache_headers=False
                )
            ])
            
            # Add the card to frontend automatically
            card_url = f"/{DOMAIN}/pool-readings-bar-card.js"
            add_extra_js_url(hass, card_url)
            
            _LOGGER.info("VirtualPoolCare frontend card registered at %s", card_url)
        else:
            _LOGGER.warning("VirtualPoolCare frontend card file not found at %s", card_file)
            
    except Exception as e:
        _LOGGER.error("Failed to register VirtualPoolCare frontend card: %s", e)