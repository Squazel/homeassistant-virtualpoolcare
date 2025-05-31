# VirtualPoolCare Integration - Testing Guide

This directory contains testing utilities and test cases for the VirtualPoolCare Home Assistant integration. You can run these tests locally without needing a full Home Assistant installation.

## Test Structure

```
tests/
├── README.md           # This file
├── __init__.py         # Test package marker
├── test_sensor.py      # Unit tests using pytest
├── test_runner.py      # Standalone test runner
└── dev_test.py         # Development/debugging utilities
```

## Prerequisites

1. **Python 3.9+** installed on your system
2. **Git** for cloning the repository

## Setup Development Environment

### 1. Clone the Repository

```bash
git clone https://github.com/Squazel/homeassistant-virtualpoolcare.git
cd homeassistant-virtualpoolcare
```

### 2. Install Development Dependencies

```bash
# Install development requirements
pip install -r requirements-dev.txt
```

This will install:
- `pytest` - Testing framework
- `pytest-asyncio` - Async testing support
- `pytest-cov` - Code coverage
- `requests` - HTTP library
- `boto3` - AWS SDK (for API authentication)

### 3. Verify Installation

```bash
# Quick verification that modules can be imported
python -c "import boto3, requests, pytest; print('✅ All dependencies installed')"
```

## Running Tests

### Option 1: Quick Test Runner (Recommended for beginners)

Run the standalone test runner that provides a simple overview:

```bash
cd tests
python test_runner.py
```

**Expected Output:**
```
Testing VirtualPoolCare Integration Components
==================================================
Domain: virtualpoolcare
Scan Interval: 6 hours

Testing data fetch...
Fetched data: {'temperature': 23.4, 'ph': 7.32, 'orp': 678, 'salinity': 3.1}

Testing sensor creation...
Created sensor: virtualpoolcare unknown temperature = 23.4
Created sensor: virtualpoolcare unknown ph = 7.32
Created sensor: virtualpoolcare unknown orp = 678
Created sensor: virtualpoolcare unknown salinity = 3.1

✅ All basic tests passed!
```

### Option 2: Development Test Suite

Run the development test suite for more detailed debugging:

```bash
cd tests
python dev_test.py
```

**Expected Output:**
```
VirtualPoolCare Integration - Development Testing
=======================================================
Simulating multiple data fetches:
----------------------------------------
Fetch 1: {
  "temperature": 24.1,
  "ph": 7.25,
  "orp": 685,
  "salinity": 3.2
}

[... more fetch results ...]

Testing sensor behavior:
------------------------------
Normal data - Temperature sensor: 78.5
Missing key - Sensor state: None
No data - Temperature sensor: None

✅ Development testing complete!
```

### Option 3: Unit Tests with pytest

Run the full unit test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ -v --cov=sensor --cov-report=html

# Run specific test file
python -m pytest tests/test_sensor.py -v
```

**Expected Output:**
```
================================ test session starts ================================
platform win32 -- Python 3.11.0, pytest-7.2.0, pluggy-1.0.0 -- python.exe
cachedir: .pytest_cache
rootdir: C:\Users\micha\Dev\HomeAssistant\homeassistant-virtualpoolcare
collected 6 items

tests/test_sensor.py::TestFetchVirtualPoolCareData::test_fetch_returns_dict PASSED
tests/test_sensor.py::TestFetchVirtualPoolCareData::test_fetch_has_expected_keys PASSED
tests/test_sensor.py::TestFetchVirtualPoolCareData::test_fetch_values_in_range PASSED
tests/test_sensor.py::TestVirtualPoolCareSensor::test_sensor_initialization PASSED
tests/test_sensor.py::TestVirtualPoolCareSensor::test_sensor_state PASSED
tests/test_sensor.py::TestVirtualPoolCareSensor::test_sensor_state_missing_key PASSED

================================ 6 passed in 0.12s =====================================
```

## What Gets Tested

### 1. Core Functionality
- ✅ Data fetching returns proper dictionary format
- ✅ Expected sensor keys are present
- ✅ Sensor values are within expected ranges
- ✅ Sensor entities are created correctly
- ✅ Unique IDs and names are generated properly

### 2. Edge Cases
- ✅ Missing sensor keys
- ✅ Empty data responses
- ✅ Invalid coordinator data

### 3. Integration Components
- ✅ Sensor state management
- ✅ Entity attribute handling
- ✅ Device serial number integration

## Mocking Strategy

The tests use comprehensive mocking to simulate Home Assistant without requiring the full framework:

```python
# Home Assistant modules are mocked
mock_ha_modules = {
    'homeassistant': MagicMock(),
    'homeassistant.components.sensor': MagicMock(),
    'homeassistant.core': MagicMock(),
    # ... etc
}
```

This allows testing of:
- Sensor creation and state management
- Data coordinator functionality
- Entity behavior and attributes

## Development Workflow

### 1. Making Changes
1. Edit source files in the root directory
2. Run tests to verify changes work
3. Add new tests for new functionality

### 2. Adding New Tests
1. Add test methods to `tests/test_sensor.py`
2. Update `dev_test.py` for interactive testing
3. Run the full test suite to ensure nothing breaks

### 3. Debugging Issues
1. Use `dev_test.py` for interactive debugging
2. Add print statements or breakpoints as needed
3. Test individual functions in isolation

## Common Issues

### ImportError: No module named 'boto3'
**Solution:** Install development dependencies
```bash
pip install -r requirements-dev.txt
```

### ModuleNotFoundError: No module named 'sensor'
**Solution:** Run tests from the `tests` directory or ensure proper path setup
```bash
cd tests
python test_runner.py
```

### Tests pass but integration fails in Home Assistant
**Solution:** The mocked environment differs from real HA. Test in a real HA instance for final validation.

## Contributing

When contributing new features:

1. **Add tests** for new functionality
2. **Run the full test suite** to ensure nothing breaks
3. **Update this README** if you add new test files or change the test structure
4. **Consider edge cases** and add tests for error conditions

## Next Steps

After your tests pass locally:

1. **Deploy to Home Assistant** for real-world testing
2. **Configure with actual credentials** in `configuration.yaml`
3. **Monitor Home Assistant logs** for any runtime issues
4. **Test with real VirtualPoolCare data** to verify API integration

## Test Data vs Real Data

**Note:** The test environment uses simulated/random data. Real integration with VirtualPoolCare will:
- Require actual login credentials
- Make real API calls to VirtualPoolCare.io
- Return actual pool sensor measurements
- Handle real network conditions and API errors

The test environment helps verify code logic and structure, but final testing should always be done with a real Home Assistant installation.