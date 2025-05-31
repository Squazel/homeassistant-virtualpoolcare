"""Standalone test runner for VirtualPoolCare integration."""
import sys
import os

# Add parent directory to path so we can import core module
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from custom_components.virtualpoolcare.virtualpoolcare_core import (
    MockVirtualPoolCareAPI, 
    VirtualPoolCareSensorData,
    DOMAIN, 
    SCAN_INTERVAL_HOURS
)

class MockSensor:
    """Simple sensor class for testing without Home Assistant dependencies."""
    
    def __init__(self, data: dict, key: str):
        self.data = data
        self._key = key
        
        device_serial = data.get("blue_device_serial", "unknown")
        self._attr_unique_id = VirtualPoolCareSensorData.create_entity_id(device_serial, key)
        self._attr_name = VirtualPoolCareSensorData.create_entity_name(device_serial, key)
        self._device_serial = device_serial
    
    @property
    def state(self):
        """Return current state."""
        return self.data.get(self._key)
    
    @property
    def native_unit_of_measurement(self):
        """Return unit of measurement."""
        return VirtualPoolCareSensorData.get_unit_of_measurement(self._key)

def test_basic_functionality():
    """Test basic functionality without Home Assistant."""
    print("Testing VirtualPoolCare Integration Components")
    print("=" * 50)
    
    # Test constants
    print(f"Domain: {DOMAIN}")
    print(f"Scan Interval: {SCAN_INTERVAL_HOURS} hours")
    
    # Test data fetching with mock API
    print("\nTesting data fetch...")
    api = MockVirtualPoolCareAPI("test@example.com", "test_password")
    data = api.fetch_data()
    print(f"Fetched data: {data}")
    
    # Test sensor creation
    print("\nTesting sensor creation...")
    sensor_keys = VirtualPoolCareSensorData.get_sensor_keys(data)
    
    for key in sensor_keys:
        sensor = MockSensor(data, key)
        print(f"Created sensor: {sensor._attr_name} = {sensor.state}")
        print(f"  - Unique ID: {sensor._attr_unique_id}")
        print(f"  - Unit: {sensor.native_unit_of_measurement}")
    
    print("\n✅ All basic tests passed!")

if __name__ == "__main__":
    test_basic_functionality()