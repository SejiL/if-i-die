import os
import time
import json
from config import COUNTDOWN_DAYS, COUNTDOWN_FILE

class Countdown:
    # Initialize the countdown timer
    def __init__(self):
        self.duration = COUNTDOWN_DAYS * 86400
        self.last_renewal = None
        self.notification_sent = False
        self.last_notification_time = None
        self.warning_sent = False
        self.last_warning_time = None
        self.load_timer()

        if self.last_renewal is None:
            self.last_renewal = time.time()
            self.save_timer()

    # Load the countdown timer from a file
    def load_timer(self):
        try:
            if os.path.exists(COUNTDOWN_FILE):
                with open(COUNTDOWN_FILE, "r") as f:
                    data = json.load(f)
                    if "last_renewal" not in data:
                        raise ValueError("Invalid timer file format")
                    self.last_renewal = data["last_renewal"]
                    self.notification_sent = data.get("notification_sent", False)
                    self.last_notification_time = data.get("last_notification_time", None)
                    self.warning_sent = data.get("warning_sent", False)
                    self.last_warning_time = data.get("last_warning_time", None)
        except FileNotFoundError:
            print("⚠️ Timer file not found. Starting new countdown.")
            self.last_renewal = None  # Will trigger file creation when saving
        except json.JSONDecodeError:
            print("⚠️ Corrupted timer file. Starting new countdown.")
            self.last_renewal = None  # Will trigger file creation when saving
        except ValueError as ve:
            print(f"⚠️ {str(ve)}. Starting new countdown.")
            self.last_renewal = None  # Will trigger file creation when saving
        except PermissionError:
            print("❌ Timer file access error")
            raise

    # Save the countdown timer to a file
    def save_timer(self):
        with open(COUNTDOWN_FILE, "w") as f:
            data = {
                "last_renewal": self.last_renewal,
                "notification_sent": self.notification_sent,
                "last_notification_time": self.last_notification_time,
                "warning_sent": self.warning_sent,
                "last_warning_time": self.last_warning_time
            }
            json.dump(data, f)

    # Renew the countdown
    def renew(self):
        self.last_renewal = time.time()
        self.notification_sent = False
        self.last_notification_time = None
        self.warning_sent = False
        self.last_warning_time = None
        self.save_timer()
        print("✅ Countdown renewed!")

    # Check if the countdown has expired
    def has_expired(self):
        return time.time() - self.last_renewal > self.duration

    def should_send_notification(self):
        """Check if we should send a notification"""
        if not self.has_expired():
            return False
            
        if not self.notification_sent:
            return True
            
        if self.last_notification_time is not None:
            time_since_last_notification = time.time() - self.last_notification_time
            return time_since_last_notification >= 86400
            
        return True

    # Mark that a notification has been sent
    def mark_notification_sent(self):
        """Mark that a notification has been sent"""
        self.notification_sent = True
        self.last_notification_time = time.time()
        self.save_timer()

    # Mark that a warning has been sent
    def mark_warning_sent(self):
        """Mark that a warning has been sent"""
        self.warning_sent = True
        self.last_warning_time = time.time()
        self.save_timer()

    # Remaining time in days, hours, minutes, seconds
    def time_left(self):
        remaining = self.duration - (time.time() - self.last_renewal)
        if remaining <= 0:
            return "⏳ Countdown expired!"
        days = int(remaining // 86400)
        hours = int((remaining % 86400) // 3600)
        minutes = int((remaining % 3600) // 60)
        seconds = int(remaining % 60)
        return f"✅ {days}d {hours}h {minutes}m {seconds}s remaining."
