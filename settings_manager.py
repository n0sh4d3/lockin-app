"""This manages my json db (i'm proud)"""

import json
import os
# ^ BOZO FORGOT TO IMPORT JSON


class SettingsManager:
    def __init__(self):
        self.settings_file = "fokus_settings.json"
        self.settings = self.load_settings()

    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        return json.loads(content)

            default_settings = {
                "theme": "system",
                "website_blocking_enabled": True,
                "blocked_sites": [
                    "facebook.com",
                    "twitter.com",
                    "instagram.com",
                    "youtube.com",
                    "tiktok.com",
                    "reddit.com",
                ],
            }
            self._write_settings(default_settings)
            return default_settings

        except Exception as e:
            print(f"Error loading settings: {e}")
            return self._get_default_settings()

    def _get_default_settings(self):
        """Get default settings"""
        return {
            "theme": "system",
            "website_blocking_enabled": True,
            "blocked_sites": [
                "facebook.com",
                "twitter.com",
                "instagram.com",
                "youtube.com",
                "tiktok.com",
                "reddit.com",
            ],
        }

    def _write_settings(self, settings_data):
        """Internal method to write settings to file"""
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(settings_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")
            raise

    def save_settings(self):
        """Save settings to file"""
        self._write_settings(self.settings)

    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)

    def set(self, key, value):
        """Set a setting value"""
        self.settings[key] = value
        self.save_settings()
