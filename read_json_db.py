import json

SESSIONS_FILE = "sessions.json"


class Database:
    def __init__(self) -> None:
        self.dates = []
        self.focus_times = []
        self.session_names = []
        self.data = {}
        self._read_json_file()
        self.load_session_names()

    def _read_json_file(self) -> None:
        """Fill in fucking json data"""
        try:
            with open(SESSIONS_FILE, "r") as file:
                self.data = json.load(file)

                if "focus_sessions" in self.data:
                    for db in self.data["focus_sessions"]:
                        self.dates.append(db["date"])
                        self.focus_times.append(db["focus_time"])

        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {"focus_sessions": [], "session_names": []}
            with open(SESSIONS_FILE, "w") as file:
                json.dump(self.data, file, indent=2)

    def save_to_json(self, date: str, focus_time: str) -> None:
        self.dates.append(date)
        self.focus_times.append(focus_time)

        session_number = len(self.session_names) + 1
        self.session_names.append(f"Session #{session_number}")

        self.data["focus_sessions"] = [
            {"date": d, "focus_time": t} for d, t in zip(self.dates, self.focus_times)
        ]
        self.data["session_names"] = self.session_names

        with open(SESSIONS_FILE, "w") as file:
            json.dump(self.data, file, indent=2)

    def save_session_names(self):
        """Save session names to the JSON file"""
        if hasattr(self, "session_names"):
            self.data["session_names"] = self.session_names
            with open(SESSIONS_FILE, "w") as file:
                json.dump(self.data, file, indent=2)

    def save_all_data(self):
        """Save all data including focus times, dates, and session names"""
        self.data["focus_sessions"] = [
            {"date": d, "focus_time": t} for d, t in zip(self.dates, self.focus_times)
        ]
        if hasattr(self, "session_names"):
            self.data["session_names"] = self.session_names

        with open(SESSIONS_FILE, "w") as file:
            json.dump(self.data, file, indent=2)

    def load_session_names(self):
        """Load session names from JSON, initialize if not present"""
        if "session_names" in self.data and self.data["session_names"]:
            self.session_names = self.data["session_names"]
        else:
            self.session_names = [
                f"Session #{i + 1}" for i in range(len(self.focus_times))
            ]
