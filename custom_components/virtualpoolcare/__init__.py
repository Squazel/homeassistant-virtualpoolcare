"""The VirtualPoolCare integration."""
from __future__ import annotations

import logging
from pathlib import Path

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType
from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig

from .const import DOMAIN, SCAN_INTERVAL_HOURS

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


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up VirtualPoolCare from a config entry."""
    # Create the coordinator here in __init__.py
    email = entry.data["email"]
    password = entry.data["password"]
    interval_hrs = entry.data.get("update_interval_hours", SCAN_INTERVAL_HOURS)
    
    from datetime import timedelta
    from .sensor import VirtualPoolCareDataUpdateCoordinator
    
    update_interval = timedelta(hours=interval_hrs)
    
    coordinator = VirtualPoolCareDataUpdateCoordinator(
        hass, 
        name=DOMAIN, 
        update_interval=update_interval,
        email=email,
        password=password
    )
    
    # THIS is where async_config_entry_first_refresh should be called
    # The config entry is still in SETUP_IN_PROGRESS state here
    await coordinator.async_config_entry_first_refresh()
    
    # Store coordinator for the sensor platform to use
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Forward setup to sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


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
            
            _LOGGER.debug("VirtualPoolCare frontend card registered at %s", card_url)
        else:
            _LOGGER.warning("VirtualPoolCare frontend card file not found at %s", card_file)
            
    except Exception as e:
        _LOGGER.error("Failed to register VirtualPoolCare frontend card: %s", e)