import yaml
import os

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    return config

config = load_config()

OWNER_NAME = config.get("owner", {}).get("name", "A person")
OWNER_EMAIL = config.get("owner", {}).get("email", "your-email@example.com")

SMTP_SERVER = config.get("smtp", {}).get("server", "smtp.example.com")
SMTP_PORT = config.get("smtp", {}).get("port", 465)
SMTP_USERNAME = config.get("smtp", {}).get("user", "your-email@example.com")
SMTP_PASSWORD = config.get("smtp", {}).get("password", "your-password")

COUNTDOWN_DAYS = config.get("countdown_days", 30)
COUNTDOWN_FILE = config.get("countdown_file", "files/countdown.json")

TRUST_PEOPLE = config.get("trust_people", {})
PEM_FOLDER = config.get("pem_folder", "files/pem")
INPUT_FOLDER = config.get("input_folder", "files/input")
ENCRYPTED_FOLDER = config.get("encrypted_folder", "files/encrypted")

os.makedirs(INPUT_FOLDER, exist_ok=True)
