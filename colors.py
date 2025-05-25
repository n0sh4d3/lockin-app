"""Light colorscheme for fokus app"""

import json
import os


class LightTheme:
    PRIMARY = "#7C4DFF"  # Vivid Purple (bold & rich)

    PRIMARY_DARK = "#651FFF"  # Deeper indigo-purple
    PRIMARY_LIGHT = "#B388FF"  # Soft highlight version

    NEUTRAL_1000 = "#FFFFFF"
    NEUTRAL_900 = "#F5F5F5"
    NEUTRAL_800 = "#E0E0E0"
    NEUTRAL_700 = "#BDBDBD"
    NEUTRAL_600 = "#9E9E9E"
    NEUTRAL_500 = "#757575"
    NEUTRAL_400 = "#616161"
    NEUTRAL_300 = "#424242"

    SUCCESS = PRIMARY
    SUCCESS_DARK = PRIMARY

    WARNING = "#FF9800"
    DANGER = "#F44336"

    FG_COLOR = "#1C1C1C"  # Strong dark text
    BG_COLOR = NEUTRAL_1000


class DarkTheme:
    PRIMARY = "#7C4DFF"  # Vivid Purple

    PRIMARY_DARK = "#512DA8"
    PRIMARY_LIGHT = "#B388FF"

    NEUTRAL_1000 = "#0D0D0D"  # Ultra dark BG
    NEUTRAL_900 = "#121212"
    NEUTRAL_800 = "#1E1E1E"
    NEUTRAL_700 = "#2A2A2A"
    NEUTRAL_600 = "#424242"
    NEUTRAL_500 = "#616161"
    NEUTRAL_400 = "#757575"
    NEUTRAL_300 = "#BDBDBD"

    SUCCESS = PRIMARY
    SUCCESS_DARK = PRIMARY

    WARNING = "#FF9800"
    DANGER = "#EF5350"

    FG_COLOR = "#F5F5F5"  # Clean light text
    BG_COLOR = NEUTRAL_1000


class SettingsManager:
    def __init__(self):
        self.settings_file = "fokus_settings.json"
        self.default_settings = {
            "theme": "dark",
            "sound_enabled": True,
            "notifications_enabled": True,
            "break_reminders": False,
        }
        self.settings = self.load_settings()

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r") as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    merged_settings = self.default_settings.copy()
                    merged_settings.update(loaded_settings)
                    return merged_settings
            else:
                return self.default_settings.copy()
        except Exception as e:
            print(f"Error loading settings: {e}")
            return self.default_settings.copy()

    def save_settings(self):
        try:
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key):
        return self.settings.get(key, self.default_settings.get(key))

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()
