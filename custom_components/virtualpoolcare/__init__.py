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

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

# Config schema - since this integration is config_entry only
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the VirtualPoolCare component."""
    # Register the frontend card
    await _async_register_frontend_card(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up VirtualPoolCare from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
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
            # Register the static path for our frontend files
            hass.http.register_static_path(
                f"/{DOMAIN}", 
                str(frontend_path), 
                cache_headers=False
            )
            
            # Add the card to frontend automatically
            card_url = f"/{DOMAIN}/pool-readings-bar-card.js"
            add_extra_js_url(hass, card_url)
            
            _LOGGER.info("VirtualPoolCare frontend card registered at %s", card_url)
        else:
            _LOGGER.warning("VirtualPoolCare frontend card file not found at %s", card_file)
            
    except Exception as e:
        _LOGGER.error("Failed to register VirtualPoolCare frontend card: %s", e)