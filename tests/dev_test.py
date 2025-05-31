"""Development testing script for VirtualPoolCare integration."""
import sys
import os
import json

# Add parent directory to path so we can import core module
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from virtualpoolcare_core import (
    VirtualPoolCareAPI,
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

def get_credentials():
    """Get credentials from environment variables or credentials file."""
    email = None
    password = None
    
    # Method 1: Try environment variables first
    email = os.getenv('VIRTUALPOOLCARE_EMAIL')
    password = os.getenv('VIRTUALPOOLCARE_PASSWORD')
    
    if email and password:
        print(f"✅ Using credentials from environment variables (email: {email})")
        return email, password
    
    # Method 2: Try credentials file
    creds_file = os.path.join(parent_dir, '.creds')
    print(creds_file)
    if os.path.exists(creds_file):
        print("FOXFOX")
        try:
            with open(creds_file, 'r') as f:
                lines = f.read().strip().split('\n')
                if len(lines) >= 2:
                    email = lines[0].strip()
                    password = lines[1].strip()
                    if email and password:
                        print(f"✅ Using credentials from .creds file (email: {email})")
                        return email, password
        except Exception as e:
            print(f"⚠️  Error reading .creds file: {e}")
    
    # No credentials found
    return None, None

def test_real_api():
    """Test the real VirtualPoolCare API with user credentials."""
    print("Testing REAL VirtualPoolCare API:")
    print("=" * 35)
    
    # Get credentials
    email, password = get_credentials()
    if not email or not password:
        print("⚠️  No credentials found - skipping real API test")
        return None
    
    try:
        print(f"\n🔄 Testing real API with email: {email}")
        
        # Create real API instance
        api = VirtualPoolCareAPI(email, password)
        
        # Test the complete fetch_data() method
        print("\nTesting complete fetch_data() method...")
        sensor_data = api.fetch_data()
        print(f"✅ Complete API test successful! Found {len(sensor_data)} data points")
        
        print(f"\nFull sensor data:")
        print(json.dumps(sensor_data, indent=2))
        
        # Test sensor creation with real data
        print("\nTesting sensor creation with REAL data:")
        print("-" * 45)
        sensor_keys = VirtualPoolCareSensorData.get_sensor_keys(sensor_data)
        
        for key in sensor_keys:
            sensor = MockSensor(sensor_data, key)
            unit_str = f" {sensor.native_unit_of_measurement}" if sensor.native_unit_of_measurement else ""
            print(f"  {sensor._attr_name} = {sensor.state}{unit_str}")
        
        print(f"\n✅ Real API test completed successfully!")
        return sensor_data
        
    except Exception as e:
        print(f"❌ Real API test failed: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print(f"Full traceback:\n{traceback.format_exc()}")
        return None

def test_mock_api():
    """Test the mock API for comparison."""
    print("Testing MOCK VirtualPoolCare API:")
    print("=" * 35)
    
    # Test API initialization
    api = MockVirtualPoolCareAPI("test@example.com", "test_password")
    print(f"MockVirtualPoolCareAPI initialized for: {api.email}")
    print(f"Core API constants: Domain={DOMAIN}, Interval={SCAN_INTERVAL_HOURS} hours")
    
    # Test data fetching
    print("\nMock data fetch:")
    data = api.fetch_data()
    print(json.dumps(data, indent=2))
    
    # Test sensor creation with mock data
    print("\nTesting sensor creation with MOCK data:")
    print("-" * 45)
    sensor_keys = VirtualPoolCareSensorData.get_sensor_keys(data)
    
    for key in sensor_keys:
        sensor = MockSensor(data, key)
        unit_str = f" {sensor.native_unit_of_measurement}" if sensor.native_unit_of_measurement else ""
        print(f"  {sensor._attr_name} = {sensor.state}{unit_str}")
    
    return data

def compare_real_vs_mock(real_data, mock_data):
    """Compare real and mock data structures."""
    if not real_data:
        return False  # Indicate no comparison was done
    
    print("\nComparing REAL vs MOCK data:")
    print("=" * 30)
    
    real_keys = set(real_data.keys())
    mock_keys = set(mock_data.keys())
    
    print(f"Real API keys: {sorted(real_keys)}")
    print(f"Mock API keys: {sorted(mock_keys)}")
    
    common_keys = real_keys & mock_keys
    only_real = real_keys - mock_keys
    only_mock = mock_keys - real_keys
    
    print(f"\nCommon keys: {sorted(common_keys)}")
    if only_real:
        print(f"Only in real data: {sorted(only_real)}")
    if only_mock:
        print(f"Only in mock data: {sorted(only_mock)}")
    
    # Check sensor keys
    real_sensor_keys = VirtualPoolCareSensorData.get_sensor_keys(real_data)
    mock_sensor_keys = VirtualPoolCareSensorData.get_sensor_keys(mock_data)
    
    print(f"\nReal sensor keys: {sorted(real_sensor_keys)}")
    print(f"Mock sensor keys: {sorted(mock_sensor_keys)}")
    
    if real_sensor_keys != mock_sensor_keys:
        print("⚠️  Warning: Real and mock sensor keys don't match!")
        print("   You may want to update the mock data to be more realistic.")
    else:
        print("✅ Real and mock sensor keys match!")
    
    return True  # Indicate comparison was done

def show_credentials_info():
    """Show information about how to provide credentials for real API testing."""
    print("\n" + "="*60)
    print("🔧 REAL API TESTING SETUP")
    print("="*60)
    print("To test against the actual VirtualPoolCare API, provide credentials:")
    print()
    print("📋 Option 1: Environment Variables (Recommended for CI)")
    print("   Windows:")
    print("     set VIRTUALPOOLCARE_EMAIL=your_email@example.com")
    print("     set VIRTUALPOOLCARE_PASSWORD=your_password")
    print("   Linux/Mac:")
    print("     export VIRTUALPOOLCARE_EMAIL=your_email@example.com")
    print("     export VIRTUALPOOLCARE_PASSWORD=your_password")
    print()
    print("📁 Option 2: Credentials File (Recommended for Local Development)")
    print("   Create a file called '.creds' in the project root containing:")
    print("     your_email@example.com")
    print("     your_password")
    print("   (Note: .creds is automatically ignored by git)")
    print()
    print("🔒 Security:")
    print("   • Credentials are never stored in code or committed to git")
    print("   • Environment variables are the most secure option")
    print("   • Real API testing makes actual calls to VirtualPoolCare.io")
    print("="*60)

def main():
    """Run development tests with both mock and real APIs."""
    print("VirtualPoolCare Integration - Development Testing")
    print("=" * 55)
    print("Testing both MOCK and REAL API functionality.\n")
    
    # Always test mock API first
    mock_data = test_mock_api()
    
    print("\n" + "="*55)
    
    # Try to test real API (no prompting)
    real_data = test_real_api()
    
    # Compare if we got real data
    did_comparison = compare_real_vs_mock(real_data, mock_data)
    
    print("\n✅ Development testing complete!")
    
    # Show credentials info if no real API test was done
    if not real_data:
        show_credentials_info()
    elif did_comparison:
        print("\n🎉 Both mock and real API tests completed successfully!")

if __name__ == "__main__":
    main()