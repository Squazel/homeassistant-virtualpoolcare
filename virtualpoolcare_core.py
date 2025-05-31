"""Core VirtualPoolCare API logic without Home Assistant dependencies."""
import logging
import json
import random

_LOGGER = logging.getLogger(__name__)

# Configuration constants
DOMAIN = "virtualpoolcare"
SCAN_INTERVAL_HOURS = 6
BASE_URL = "https://vpc.virtualpoolcare.io/prod"


class VirtualPoolCareAPI:
    """Core API client for VirtualPoolCare without Home Assistant dependencies."""
    
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
    
    def login_to_virtualpoolcare(self) -> dict:
        """
        Step 1: Login to VirtualPoolCare and get AWS credentials.
        
        Returns:
            dict: Contains access_key, secret_key, session_token, region
        """
        import requests
        
        login_url = f"{BASE_URL}/user/login"
        login_data = {
            "email": self.email,
            "password": self.password
        }
        
        # TODO: Handle error responses (401, 403, 500, etc.)
        response = requests.post(login_url, json=login_data)
        response.raise_for_status()
        
        json_data = response.json()
        credentials = json_data["credentials"]
        identity_id = json_data["identity_id"]
        
        return {
            "access_key": credentials["access_key"],
            "secret_key": credentials["secret_key"],
            "session_token": credentials["session_token"],
            "region": identity_id.split(':')[0]
        }

    def make_authenticated_request(self, url: str, method: str, credentials: dict, payload: str = "") -> dict:
        """
        Make authenticated API request using boto3 for AWS signature.
        
        Args:
            url: Full URL to request
            method: HTTP method (GET, POST, etc.)
            credentials: AWS credentials from login
            payload: Request body (empty string for GET)
            
        Returns:
            dict: JSON response
        """
        import boto3
        from botocore.auth import SigV4Auth
        from botocore.awsrequest import AWSRequest
        import requests
        
        # Create boto3 session with temporary credentials
        session = boto3.Session(
            aws_access_key_id=credentials["access_key"],
            aws_secret_access_key=credentials["secret_key"],
            aws_session_token=credentials["session_token"],
            region_name=credentials["region"]
        )
        
        # Create AWS request object
        request = AWSRequest(method=method, url=url, data=payload)
        request.headers['Content-Type'] = 'application/json'
        
        # Sign the request
        SigV4Auth(session.get_credentials(), "execute-api", credentials["region"]).add_auth(request)
        
        # Make the actual HTTP request
        response = requests.request(
            method=request.method,
            url=request.url,
            headers=dict(request.headers),
            data=request.body
        )
        
        # TODO: Handle error responses
        response.raise_for_status()
        return response.json()

    def get_pools_list(self, credentials: dict) -> dict:
        """
        Step 2: Get list of pools from VirtualPoolCare.
        
        Args:
            credentials: AWS credentials from login step
            
        Returns:
            dict: Contains pool_id and blue_key for first pool
        """
        pools_url = f"{BASE_URL}/pools?page=1&results=15&sortField=user_lastname&sortOrder=ASC"
        
        json_data = self.make_authenticated_request(pools_url, "GET", credentials)
        
        # TODO: Handle pagination if > 15 results
        # TODO: Loop through all results instead of just taking first
        first_pool = json_data["data"][0]
        
        return {
            "pool_id": first_pool["pool_id"],
            "blue_key": first_pool["blue_key"]
        }

    def get_pool_measurements(self, credentials: dict, pool_id: str, blue_key: str) -> dict:
        """
        Step 3: Get latest measurements for a specific pool.
        
        Args:
            credentials: AWS credentials from login step
            pool_id: Pool ID from pools list
            blue_key: Blue device key from pools list
            
        Returns:
            dict: Latest sensor measurements
        """
        measurements_url = f"{BASE_URL}/swimming_pool/{pool_id}/blue/{blue_key}/lastMeasurements"
        
        return self.make_authenticated_request(measurements_url, "GET", credentials)

    def parse_measurements_data(self, measurements_response: dict) -> dict:
        """
        Step 4: Parse measurements response into sensor format.
        
        Args:
            measurements_response: Raw API response from lastMeasurements
            
        Returns:
            dict: Sensor data in format {sensor_name: value}
        """
        sensor_data = {}
        
        if measurements_response.get("status") != "OK":
            _LOGGER.warning("Measurements response status not OK: %s", measurements_response.get("status"))
            return sensor_data
        
        # Add metadata
        sensor_data["blue_device_serial"] = measurements_response.get("blue_device_serial")
        sensor_data["last_measurement_timestamp"] = measurements_response.get("last_blue_measure_timestamp")
        
        # Parse measurement data
        for measurement in measurements_response.get("data", []):
            name = measurement.get("name")
            value = measurement.get("value")
            timestamp = measurement.get("timestamp")
            expired = measurement.get("expired", False)
            
            if name and value is not None:
                sensor_data[name] = value
                sensor_data[f"{name}_timestamp"] = timestamp
                sensor_data[f"{name}_expired"] = expired
                
                # Add trend if available
                trend = measurement.get("trend")
                if trend and trend != "undefined":
                    sensor_data[f"{name}_trend"] = trend
        
        return sensor_data

    def fetch_data(self) -> dict:
        """
        Main function to fetch all VirtualPoolCare data.
        
        Returns:
            dict: Complete sensor data
        """
        try:
            # Step 1: Login and get credentials
            _LOGGER.info("Logging into VirtualPoolCare...")
            credentials = self.login_to_virtualpoolcare()
            
            # Step 2: Get pools list
            _LOGGER.info("Getting pools list...")
            pool_info = self.get_pools_list(credentials)
            
            # Step 3: Get measurements
            _LOGGER.info("Getting pool measurements...")
            measurements = self.get_pool_measurements(
                credentials, 
                pool_info["pool_id"], 
                pool_info["blue_key"]
            )
            
            # Step 4: Parse and return data
            _LOGGER.info("Parsing measurement data...")
            sensor_data = self.parse_measurements_data(measurements)
            
            _LOGGER.info("Successfully fetched VirtualPoolCare data: %s sensors", len(sensor_data))
            return sensor_data
            
        except Exception as e:
            _LOGGER.error("Error fetching VirtualPoolCare data: %s", str(e))
            raise


class MockVirtualPoolCareAPI(VirtualPoolCareAPI):
    """Mock version for testing that returns fake data."""
    
    def fetch_data(self) -> dict:
        """Return mock data for testing."""
        _LOGGER.info(f"Mock fetching VirtualPoolCare data for {self.email}...")
        
        return {
            "temperature": round(random.uniform(20.0, 30.0), 1),
            "ph": round(random.uniform(7.0, 8.0), 2),
            "orp": round(random.uniform(600, 800), 0),
            "salinity": round(random.uniform(2.5, 4.0), 1),
            "blue_device_serial": "0A2B3C4D",
            "last_measurement_timestamp": "2024-01-01T12:00:00Z"
        }


class VirtualPoolCareSensorData:
    """Helper class for sensor data management."""
    
    @staticmethod
    def get_sensor_keys(data: dict) -> set:
        """Get keys that should become sensors (exclude metadata)."""
        excluded_keys = {
            "blue_device_serial", 
            "last_measurement_timestamp"
        }
        
        return {
            key for key in data.keys() 
            if not key.endswith(('_timestamp', '_expired', '_trend')) 
            and key not in excluded_keys
        }
    
    @staticmethod
    def get_unit_of_measurement(sensor_key: str) -> str:
        """Get unit of measurement for a sensor key."""
        unit_mapping = {
            "temperature": "°C",
            "ph": None,
            "orp": "mV",
            "salinity": "g/L",
            "chlorine_ppm": "ppm",
            "chlorine": "ppm",
            "tds": "ppm",
            "conductivity": "µS/cm"
        }
        return unit_mapping.get(sensor_key, None)
    
    @staticmethod
    def create_entity_id(device_serial: str, sensor_key: str) -> str:
        """Create unique entity ID."""
        return f"{DOMAIN}_{device_serial}_{sensor_key}"
    
    @staticmethod
    def create_entity_name(device_serial: str, sensor_key: str) -> str:
        """Create human-readable entity name."""
        return f"{DOMAIN} {device_serial} {sensor_key}"