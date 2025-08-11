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
        self.api_url = "https://signage-be.miz.cab/output.json"
        self.use_local = use_local
        self.load_config()

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
        try:
            print(f"Loading config from {self.api_url}")
            with urllib.request.urlopen(self.api_url, timeout=5) as response:
                self.config_data = json.loads(response.read().decode("utf-8"))
                print("Successfully loaded remote config")
                return True
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
        return self.config_data.get(key)

    def reload(self) -> None:
        """Reload configuration from file or API."""
        self.load_config()
