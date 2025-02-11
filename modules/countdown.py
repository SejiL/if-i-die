import os
import time
import json
import argparse
from config import COUNTDOWN_DAYS, COUNTDOWN_FILE

class Countdown:
    def __init__(self):
        self.duration = COUNTDOWN_DAYS * 86400  # Convert days to seconds
        self.load_timer()

    def load_timer(self):
        try:
            if os.path.exists(COUNTDOWN_FILE):
                with open(COUNTDOWN_FILE, "r") as f:
                    data = json.load(f)
                    self.last_renewal = data.get("last_renewal", time.time())
            else:
                raise FileNotFoundError
        except (FileNotFoundError, json.JSONDecodeError):
            print("⚠️ Timer file missing or corrupt. Resetting countdown.")
            self.last_renewal = time.time()
            self.save_timer()

    def save_timer(self):
        with open(COUNTDOWN_FILE, "w") as f:
            json.dump({"last_renewal": self.last_renewal}, f)

    def renew(self):
        self.last_renewal = time.time()
        self.save_timer()
        print("✅ Countdown renewed!")

    def has_expired(self):
        return time.time() - self.last_renewal > self.duration

    def time_left(self):
        remaining = self.duration - (time.time() - self.last_renewal)
        if remaining <= 0:
            return "⏳ Countdown expired!"
        days = int(remaining // 86400)
        hours = int((remaining % 86400) // 3600)
        minutes = int((remaining % 3600) // 60)
        return f"✅ {days}d {hours}h {minutes}m remaining."

