"""The VirtualPoolCare integration."""
from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


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
        card_path = frontend_path / "pool-readings-bar-card.js"
        
        if card_path.exists():
            # Register the card as a frontend resource
            hass.http.register_static_path(
                "/virtualpoolcare-card", 
                str(frontend_path), 
                cache_headers=False
            )
            
            # Add to Lovelace resources automatically
            if "lovelace" in hass.data:
                resources = hass.data["lovelace"].get("resources", [])
                card_url = "/virtualpoolcare-card/pool-readings-bar-card.js"
                
                # Check if already registered
                if not any(resource.get("url") == card_url for resource in resources):
                    resources.append({
                        "url": card_url,
                        "type": "module"
                    })
                    
            _LOGGER.info("VirtualPoolCare frontend card registered successfully")
        else:
            _LOGGER.warning("VirtualPoolCare frontend card file not found")
            
    except Exception as e:
        _LOGGER.error("Failed to register VirtualPoolCare frontend card: %s", e)