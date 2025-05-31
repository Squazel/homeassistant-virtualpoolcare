"""Test the VirtualPoolCare sensor platform."""
import unittest
from unittest.mock import Mock, AsyncMock, patch
import asyncio
from datetime import timedelta

# Mock Home Assistant modules before importing our code
import sys
from unittest.mock import MagicMock

# Create mock modules
mock_ha_modules = {
    'homeassistant': MagicMock(),
    'homeassistant.components': MagicMock(),
    'homeassistant.components.sensor': MagicMock(),
    'homeassistant.core': MagicMock(),
    'homeassistant.helpers': MagicMock(),
    'homeassistant.helpers.update_coordinator': MagicMock(),
    'homeassistant.helpers.entity_platform': MagicMock(),
    'homeassistant.helpers.typing': MagicMock(),
}

for module_name, mock_module in mock_ha_modules.items():
    sys.modules[module_name] = mock_module

# Now we can import our code
from custom_components.virtualpoolcare.sensor import (
    VirtualPoolCareDataUpdateCoordinator,
    VirtualPoolCareSensor,
    fetch_virtualpoolcare_data,
    _add_new_virtualpoolcare_entities
)
from custom_components.virtualpoolcare.const import DOMAIN, SCAN_INTERVAL_HOURS


class TestFetchVirtualPoolCareData(unittest.TestCase):
    """Test the data fetching function."""

    def test_fetch_returns_dict(self):
        """Test that fetch function returns a dictionary."""
        result = fetch_virtualpoolcare_data()
        self.assertIsInstance(result, dict)

    def test_fetch_has_expected_keys(self):
        """Test that fetch function returns expected keys."""
        result = fetch_virtualpoolcare_data()
        expected_keys = {"water_temperature", "pH_level", "chlorine_ppm"}
        self.assertTrue(expected_keys.issubset(result.keys()))

    def test_fetch_values_in_range(self):
        """Test that fetched values are in expected ranges."""
        result = fetch_virtualpoolcare_data()
        
        # Test temperature range
        self.assertGreaterEqual(result["water_temperature"], 75.0)
        self.assertLessEqual(result["water_temperature"], 85.0)
        
        # Test pH range
        self.assertGreaterEqual(result["pH_level"], 7.0)
        self.assertLessEqual(result["pH_level"], 8.0)
        
        # Test chlorine range
        self.assertGreaterEqual(result["chlorine_ppm"], 0.5)
        self.assertLessEqual(result["chlorine_ppm"], 3.0)


class TestVirtualPoolCareSensor(unittest.TestCase):
    """Test the VirtualPoolCare sensor."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_coordinator = Mock()
        self.mock_coordinator.data = {
            "water_temperature": 78.5,
            "pH_level": 7.2,
            "chlorine_ppm": 1.5
        }
        # Add the available property that the sensor checks
        self.mock_coordinator.last_update_success = True
        self.sensor = VirtualPoolCareSensor(self.mock_coordinator, "water_temperature")

    def test_sensor_initialization(self):
        """Test sensor is initialized correctly."""
        self.assertEqual(self.sensor._key, "water_temperature")
        self.assertEqual(self.sensor._attr_unique_id, f"{DOMAIN}_water_temperature")
        self.assertEqual(self.sensor._attr_name, f"{DOMAIN} water_temperature")

    def test_sensor_state(self):
        """Test sensor returns correct state."""
        self.assertEqual(self.sensor.state, 78.5)

    def test_sensor_state_missing_key(self):
        """Test sensor returns None for missing key."""
        sensor = VirtualPoolCareSensor(self.mock_coordinator, "missing_key")
        self.assertIsNone(sensor.state)

    def test_sensor_state_no_data(self):
        """Test sensor returns None when coordinator has no data."""
        self.mock_coordinator.data = None
        self.assertIsNone(self.sensor.state)

    def test_sensor_available_property(self):
        """Test sensor availability property."""
        # Should be available when coordinator has successful update
        self.assertTrue(self.sensor.available)
        
        # Should be unavailable when coordinator update failed
        self.mock_coordinator.last_update_success = False
        self.assertFalse(self.sensor.available)


class TestVirtualPoolCareDataUpdateCoordinator(unittest.TestCase):
    """Test the data update coordinator."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_hass = Mock()
        self.coordinator = VirtualPoolCareDataUpdateCoordinator(self.mock_hass)

    def test_coordinator_initialization(self):
        """Test coordinator is initialized correctly."""
        self.assertEqual(self.coordinator.name, "VirtualPoolCare")
        self.assertEqual(self.coordinator.update_interval, timedelta(hours=SCAN_INTERVAL_HOURS))

    async def test_coordinator_update_data(self):
        """Test coordinator data update."""
        # This is an async test
        data = await self.coordinator._async_update_data()
        self.assertIsInstance(data, dict)
        expected_keys = {"water_temperature", "pH_level", "chlorine_ppm"}
        self.assertTrue(expected_keys.issubset(data.keys()))


if __name__ == "__main__":
    unittest.main()