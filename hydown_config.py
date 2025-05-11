import os
import json

CONFIG_FILE = "hydown_config.json"
DEFAULT_DOWNLOAD_DIR = os.path.join(os.getcwd(), "HyDown_Downloads") 
DEFAULT_MAX_CONCURRENT_DOWNLOADS = 3
DEFAULT_APPEARANCE_MODE = "system"

def load_settings():
    """Loads settings from the config file or returns defaults."""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                loaded_config = json.load(f)
                settings = {
                    "download_dir": loaded_config.get("download_dir", DEFAULT_DOWNLOAD_DIR),
                    "max_concurrent_downloads": loaded_config.get("max_concurrent_downloads", DEFAULT_MAX_CONCURRENT_DOWNLOADS),
                    "appearance_mode": loaded_config.get("appearance_mode", DEFAULT_APPEARANCE_MODE)
                }
                return settings
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading config file '{CONFIG_FILE}': {e}. Using defaults.")
    

    return {
        "download_dir": DEFAULT_DOWNLOAD_DIR,
        "max_concurrent_downloads": DEFAULT_MAX_CONCURRENT_DOWNLOADS,
        "appearance_mode": DEFAULT_APPEARANCE_MODE
    }

def save_settings_to_file(settings_dict):
    """Saves the provided settings dictionary to the config file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(settings_dict, f, indent=4)
        print(f"Settings saved to {CONFIG_FILE}")
        return True
    except IOError as e:
        print(f"Error saving config file '{CONFIG_FILE}': {e}")
        return False

def ensure_download_dir_exists(download_dir_path):
    """Creates the download directory if it doesn't exist."""
    if not os.path.exists(download_dir_path):
        try:
            os.makedirs(download_dir_path, exist_ok=True)
            print(f"Created download directory: {download_dir_path}")
        except OSError as e:
            print(f"Could not create download directory: {download_dir_path}. Error: {e}")
            return False
    return True

