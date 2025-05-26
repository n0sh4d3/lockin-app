class SettingsManager:
    def __init__(self):
        self.settings_file = "fokus_settings.json"
        self.settings = self.load_settings()

    def load_settings(self):
        """Load settings from file"""
        try:
            with open(self.settings_file, "r") as f:
                return json.load(f)
        except:
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
        except:
            pass

    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)

    def set(self, key, value):
        """Set a setting value"""
        self.settings[key] = value
        self.save_settings()

