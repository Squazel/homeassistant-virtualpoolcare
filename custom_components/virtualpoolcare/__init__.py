"""VirtualPoolCare Integration for Home Assistant."""

# Handle case where homeassistant module might not be available (during testing)
try:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers import config_validation as cv
    from .const import DOMAIN
    
    # Define config schema - this integration uses config entry only
    CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
    
except ImportError:
    # This allows the module to be imported during testing without Home Assistant
    HomeAssistant = None
    CONFIG_SCHEMA = None
    from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the VirtualPoolCare integration."""
    if hass is not None:
        hass.data.setdefault(DOMAIN, {})
    return True