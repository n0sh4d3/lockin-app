import json

SESSIONS_FILE = "sessions.json"


class Database:
    def __init__(self) -> None:
        self.dates = []
        self.focus_times = []
        self._read_json_file()

    def _read_json_file(self) -> None:
        """Fill in fucking json data"""
        try:
            with open(SESSIONS_FILE, "r") as file:
                data = json.load(file)
                for db in data["focus_sessions"]:
                    self.dates.append(db["date"])
                    self.focus_times.append(db["focus_time"])
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"focus_sessions": []}
            with open(SESSIONS_FILE, "w") as file:
                json.dump(data, file, indent=2)

    def save_to_json(self, date: str, focus_time: str) -> None:
        self.dates.append(date)
        self.focus_times.append(focus_time)

        data = {
            "focus_sessions": [
                {"date": d, "focus_time": t}
                for d, t in zip(self.dates, self.focus_times)
            ]
        }

        with open(SESSIONS_FILE, "w") as file:
            json.dump(data, file, indent=2)
