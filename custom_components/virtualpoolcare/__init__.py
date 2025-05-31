"""VirtualPoolCare Integration for Home Assistant."""

# Handle case where homeassistant module might not be available (during testing)
try:
    from homeassistant.core import HomeAssistant
    from .const import DOMAIN
except ImportError:
    # This allows the module to be imported during testing without Home Assistant
    HomeAssistant = None
    from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the VirtualPoolCare integration."""
    if hass is not None:
        hass.data.setdefault(DOMAIN, {})
    return True