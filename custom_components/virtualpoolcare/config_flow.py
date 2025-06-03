"""Config flow for VirtualPoolCare integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .virtualpoolcare_core import VirtualPoolCareAPI

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("email"): str,
        vol.Required("password"): str,
        vol.Optional("update_interval_hours", default=6): vol.All(vol.Coerce(int), vol.Range(min=1, max=24)),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # Test the connection
    api = VirtualPoolCareAPI(data["email"], data["password"])
    
    try:
        # Test authentication by trying to fetch data
        result = await hass.async_add_executor_job(api.fetch_data)
        if not result:
            raise InvalidAuth
        
        # Get device serial for unique ID
        device_serial = result.get("blue_device_serial", "unknown")
        if device_serial == "unknown":
            _LOGGER.warning("No device serial found in API response")
        
    except InvalidAuth:
        raise
    except Exception as exc:
        _LOGGER.exception("Unexpected exception during validation")
        raise CannotConnect from exc

    # Return info that you want to store in the config entry.
    return {
        "title": f"VirtualPoolCare Pool ({device_serial})",
        "device_serial": device_serial
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for VirtualPoolCare."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Set unique ID based on device serial
                await self.async_set_unique_id(info["device_serial"])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""