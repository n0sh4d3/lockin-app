import json
import os


class SettingsManager:
    def __init__(self):
        self.settings_file = "fokus_settings.json"
        self.settings = self.load_settings()

    def load_settings(self):
        """Load settings from file"""
        try:
            with open(self.settings_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Settings file not found, creating default settings")
            return self._default_settings()
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return self._default_settings()
        except Exception as e:
            print(f"Unexpected error loading settings: {e}")
            return self._default_settings()

    def _default_settings(self):
        """Return default settings"""
        return {
            "theme": "system",
            "website_blocking_enabled": False,
            "blocked_sites": [
                "facebook.com",
                "twitter.com",
                "instagram.com",
                "youtube.com",
                "tiktok.com",
                "reddit.com",
            ],
        }

    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f, indent=2)
            return True

        except PermissionError:
            print(f"Permission denied: Cannot write to {self.settings_file}")
            return False
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False

    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)

    def set(self, key, value):
        """Set a setting value"""
        self.settings[key] = value
        success = self.save_settings()
        if not success:
            print(f"Warning: Failed to save setting {key}={value}")
