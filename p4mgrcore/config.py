"""Configuration management for P4Mgr."""

import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


class Config:
    """Configuration manager for display settings."""

    def __init__(
        self, config_path: str | Path = "config.json", use_local: bool = False
    ):
        """Initialize configuration manager.

        Args:
            config_path: Path to configuration JSON file.
            use_local: Force use of local config file.
        """
        self.config_path = Path(config_path)
        self.config_data: dict[str, Any] = {}
        self.api_url = None  # Will be loaded from config
        self.api_key = None  # Will be loaded from config
        self.use_local = use_local
        self._load_initial_config()
        self.load_config()

    def _load_initial_config(self) -> None:
        """Load initial configuration to get API URL and key."""
        if self.config_path.exists():
            try:
                with open(self.config_path, encoding="utf-8") as f:
                    initial_config = json.load(f)
                    # Get API URL from config
                    if "api_url" in initial_config:
                        self.api_url = initial_config["api_url"]
                        print(f"API URL configured: {self.api_url}")
                    else:
                        # Default fallback
                        self.api_url = "https://signage-be.miz.cab/output.json"
                        print("Using default API URL")
                    
                    # Get API key from config
                    if "api_key" in initial_config:
                        self.api_key = initial_config["api_key"]
                        print("API key configured")
                    else:
                        print("No API key configured - authentication disabled")
            except Exception as e:
                print(f"Error loading initial config: {e}")
                self.api_url = "https://signage-be.miz.cab/output.json"
        else:
            # Default if no config file
            self.api_url = "https://signage-be.miz.cab/output.json"
            print("No config file found, using default API URL")

    def load_config(self) -> None:
        """Load configuration from JSON file or API."""
        if self.use_local:
            self._load_local_config()
        else:
            # Try API first, fall back to cached data or local on failure
            if not self._load_remote_config():
                if self.config_data:
                    print("Failed to load remote config, using cached data")
                else:
                    print("Failed to load remote config, using local config")
                    self._load_local_config()

    def _load_local_config(self) -> None:
        """Load configuration from local JSON file."""
        if self.config_path.exists():
            with open(self.config_path, encoding="utf-8") as f:
                self.config_data = json.load(f)
                print(f"Loaded local config from {self.config_path}")
        else:
            self.config_data = {}
            print(f"Local config file {self.config_path} not found")

    def _load_remote_config(self) -> bool:
        """Load configuration from remote API.

        Returns:
            True if successful, False otherwise.
        """
        if not self.api_url:
            print("No API URL configured, skipping remote config")
            return False
            
        try:
            print(f"Loading config from {self.api_url}")
            headers = {'User-Agent': 'P4Mgr/1.0'}
            
            # Add API key to headers if configured
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
                # If API key is configured, use secure endpoint
                if self.api_url.endswith('/output.json'):
                    secure_url = self.api_url.replace('/output.json', '/output.json/secure')
                    print(f"Using secure endpoint: {secure_url}")
                    self.api_url = secure_url
            
            request = urllib.request.Request(self.api_url, headers=headers)
            with urllib.request.urlopen(request, timeout=5) as response:
                raw_data = response.read().decode("utf-8")
                self.config_data = json.loads(raw_data)
                print(f"Successfully loaded remote config (size: {len(raw_data)} bytes)")
                print(f"Available display codes: {list(self.config_data.keys())}")
                return True
        except urllib.error.HTTPError as e:
            print(f"HTTP error {e.code}: {e.reason}")
            if e.code == 401:
                print("Authentication failed - check your API key")
            return False
        except urllib.error.URLError as e:
            print(f"Network error: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error loading remote config: {e}")
            return False

    def get_display_config(self, key: str) -> dict[str, Any] | None:
        """Get display configuration for given key.

        Args:
            key: Display configuration key (e.g., "01", "02").

        Returns:
            Display configuration dict or None if not found.
        """
        # Check if config_data has a "displays" section (local format)
        if "displays" in self.config_data:
            return self.config_data["displays"].get(key)
        else:
            # Direct key access (API format)
            return self.config_data.get(key)

    def reload(self) -> None:
        """Reload configuration from file or API."""
        self.load_config()
