"""Standalone test runner for VirtualPoolCare integration."""
import sys
import os
from unittest.mock import MagicMock

# Add parent directory to path so we can import our modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Mock Home Assistant modules
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

# Import and test our modules
from sensor import fetch_virtualpoolcare_data, VirtualPoolCareSensor
from const import DOMAIN, SCAN_INTERVAL_HOURS

def test_basic_functionality():
    """Test basic functionality without Home Assistant."""
    print("Testing VirtualPoolCare Integration Components")
    print("=" * 50)
    
    # Test constants
    print(f"Domain: {DOMAIN}")
    print(f"Scan Interval: {SCAN_INTERVAL_HOURS} hours")
    
    # Test data fetching
    print("\nTesting data fetch...")
    data = fetch_virtualpoolcare_data()
    print(f"Fetched data: {data}")
    
    # Test sensor creation (with mocked coordinator)
    print("\nTesting sensor creation...")
    from unittest.mock import Mock
    
    mock_coordinator = Mock()
    mock_coordinator.data = data
    
    for key in data.keys():
        sensor = VirtualPoolCareSensor(mock_coordinator, key)
        print(f"Created sensor: {sensor._attr_name} = {sensor.state}")
    
    print("\n✅ All basic tests passed!")

if __name__ == "__main__":
    test_basic_functionality()