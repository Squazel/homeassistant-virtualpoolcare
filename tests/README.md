# VirtualPoolCare Integration - Testing Guide

This directory contains testing utilities and test cases for the VirtualPoolCare Home Assistant integration. You can run these tests locally without needing a full Home Assistant installation.

## Testing Approaches

The integration supports **two levels of testing**:

1. **Mock Testing** - Fast tests using fake data (no credentials needed)
2. **Real API Testing** - Tests against actual VirtualPoolCare API (automatic if credentials provided)

## Architecture Overview

The integration uses a clean separation of concerns:

```
homeassistant-virtualpoolcare/
├── virtualpoolcare_core.py    # Core API logic (no HA dependencies)
├── sensor.py                  # Home Assistant integration wrapper
├── const.py                   # Configuration constants
├── .creds                     # Credentials file (optional, not committed)
└── tests/
    ├── test_runner.py         # Mock testing only
    ├── dev_test.py           # Both mock AND real API testing
    └── test_sensor.py        # Unit tests using pytest
```

## Prerequisites

1. **Python 3.9+** installed on your system
2. **Git** for cloning the repository
3. **VirtualPoolCare account** (optional, for real API testing)

## Setup Development Environment

### 1. Clone the Repository

```bash
git clone https://github.com/Squazel/homeassistant-virtualpoolcare.git
cd homeassistant-virtualpoolcare
```

### 2. Install Development Dependencies

```bash
# Install development requirements (from project root)
pip install -r requirements-dev.txt
```

### 3. (Optional) Setup Credentials for Real API Testing

You can provide VirtualPoolCare credentials in two ways:

#### Option A: Environment Variables (Recommended for CI)
```bash
# Windows
set VIRTUALPOOLCARE_EMAIL=your_email@example.com
set VIRTUALPOOLCARE_PASSWORD=your_password

# Linux/Mac
export VIRTUALPOOLCARE_EMAIL=your_email@example.com
export VIRTUALPOOLCARE_PASSWORD=your_password
```

#### Option B: Credentials File (Recommended for Local Development)
Create a file called `.creds` in the project root:
```
your_email@example.com
your_password
```
**Note:** This file is automatically ignored by git and won't be committed.

### 4. Verify Installation

```bash
# Quick verification that modules can be imported
python -c "import boto3, requests, pytest; print('✅ All dependencies installed')"
```

## Running Tests

**Important:** All commands should be run from the project root directory, not the tests directory.

### Option 1: Mock Testing Only (Fastest)

For quick validation without credentials:

```bash
# From project root
python tests/test_runner.py
```

### Option 2: Comprehensive Testing (Mock + Real API)

Automatically tests both mock and real APIs (if credentials are provided):

```bash
# From project root
python tests/dev_test.py
```

**With Credentials:**
```
VirtualPoolCare Integration - Development Testing
=======================================================

Testing MOCK VirtualPoolCare API:
===================================
MockVirtualPoolCareAPI initialized for: test@example.com
Mock data fetch:
{
  "temperature": 24.1,
  "ph": 7.25,
  "orp": 685,
  "salinity": 3.2,
  "blue_device_serial": "0A2B3C4D"
}

Testing sensor creation with MOCK data:
---------------------------------------------
  virtualpoolcare 0A2B3C4D temperature = 24.1 °C
  virtualpoolcare 0A2B3C4D ph = 7.25
  virtualpoolcare 0A2B3C4D orp = 685 mV
  virtualpoolcare 0A2B3C4D salinity = 3.2 g/L

Testing REAL VirtualPoolCare API:
==================================
✅ Using credentials from .creds file (email: your_email@example.com)

🔄 Testing real API with email: your_email@example.com

Testing complete fetch_data() method...
✅ Complete API test successful! Found 8 data points

Comparing REAL vs MOCK data:
==============================
✅ Real and mock sensor keys match!

✅ Development testing complete!

🎉 Both mock and real API tests completed successfully!
```

**Without Credentials:**
```
VirtualPoolCare Integration - Development Testing
=======================================================

Testing MOCK VirtualPoolCare API:
===================================
[... mock test output ...]

Testing REAL VirtualPoolCare API:
==================================
⚠️  No credentials found - skipping real API test

✅ Development testing complete!

============================================================
🔧 REAL API TESTING SETUP
============================================================
To test against the actual VirtualPoolCare API, provide credentials:

📋 Option 1: Environment Variables (Recommended for CI)
   Windows:
     set VIRTUALPOOLCARE_EMAIL=your_email@example.com
     set VIRTUALPOOLCARE_PASSWORD=your_password
   Linux/Mac:
     export VIRTUALPOOLCARE_EMAIL=your_email@example.com
     export VIRTUALPOOLCARE_PASSWORD=your_password

📁 Option 2: Credentials File (Recommended for Local Development)
   Create a file called '.creds' in the project root containing:
     your_email@example.com
     your_password
   (Note: .creds is automatically ignored by git)

🔒 Security:
   • Credentials are never stored in code or committed to git
   • Environment variables are the most secure option
   • Real API testing makes actual calls to VirtualPoolCare.io
============================================================
```

### Option 3: Unit Tests with pytest

Run the full automated test suite:

```bash
# Run all tests (from project root)
python -m pytest tests/ -v
```

## Real API Testing Benefits

Testing against the real API helps you:

1. **Validate credentials** - Ensure your VirtualPoolCare login works
2. **Check data format** - Verify the API returns expected data structure
3. **Test error handling** - See how the code handles real network issues
4. **Validate parsing** - Ensure mock data matches real data format

## Security Notes

- **Credentials are never stored in code or committed to git**
- **Environment variables are the most secure option**
- **The .creds file is automatically ignored by git**
- **Real API testing makes actual calls which may count against rate limits**
- **No interactive prompting - tests run automatically if credentials are found**

## Development Workflow

### 1. Start with Mock Testing
```bash
python tests/test_runner.py
```
Fast feedback for code changes.

### 2. Comprehensive Testing (if you have credentials)
```bash
python tests/dev_test.py
```
Automatically tests both mock and real APIs if credentials are available.

### 3. Run Unit Tests
```bash
python -m pytest tests/ -v
```
Ensure all automated tests pass.

### 4. Deploy to Home Assistant
Test in real HA environment with actual configuration.

The modular architecture makes it easy to test changes in isolation before deploying to Home Assistant!