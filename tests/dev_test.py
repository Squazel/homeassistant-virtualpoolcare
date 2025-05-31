"""Development testing script for VirtualPoolCare integration."""
import sys
import os
import json
from unittest.mock import MagicMock

# Setup mocking before imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Mock Home Assistant modules
mock_modules = {
    'homeassistant': MagicMock(),
    'homeassistant.components': MagicMock(),
    'homeassistant.components.sensor': MagicMock(),
    'homeassistant.core': MagicMock(),
    'homeassistant.helpers': MagicMock(),
    'homeassistant.helpers.update_coordinator': MagicMock(),
    'homeassistant.helpers.entity_platform': MagicMock(),
    'homeassistant.helpers.typing': MagicMock(),
}

for name, mock in mock_modules.items():
    sys.modules[name] = mock

# Now import our code
from sensor import fetch_virtualpoolcare_data, VirtualPoolCareSensor
from const import DOMAIN

def simulate_data_fetch():
    """Simulate multiple data fetches to see variation."""
    print("Simulating multiple data fetches:")
    print("-" * 40)
    
    for i in range(5):
        data = fetch_virtualpoolcare_data()
        print(f"Fetch {i+1}: {json.dumps(data, indent=2)}")
        print()

def test_sensor_behavior():
    """Test sensor behavior with different data scenarios."""
    from unittest.mock import Mock
    
    print("Testing sensor behavior:")
    print("-" * 30)
    
    # Test with normal data
    mock_coordinator = Mock()
    mock_coordinator.data = {
        "water_temperature": 78.5,
        "pH_level": 7.2,
        "chlorine_ppm": 1.5
    }
    
    sensor = VirtualPoolCareSensor(mock_coordinator, "water_temperature")
    print(f"Normal data - Temperature sensor: {sensor.state}")
    
    # Test with missing key
    sensor_missing = VirtualPoolCareSensor(mock_coordinator, "missing_sensor")
    print(f"Missing key - Sensor state: {sensor_missing.state}")
    
    # Test with no data
    mock_coordinator.data = None
    print(f"No data - Temperature sensor: {sensor.state}")

def main():
    """Run all development tests."""
    print("VirtualPoolCare Integration - Development Testing")
    print("=" * 55)
    
    simulate_data_fetch()
    test_sensor_behavior()
    
    print("\n✅ Development testing complete!")

if __name__ == "__main__":
    main()