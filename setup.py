import os
import json
from pathlib import Path

FOLDER = "/etc/libinput"
FILE = "/etc/libinput/local-overrides.quirks"
DEVICE_FILE = Path(__file__).parent / "devices.json"


def _load_device_names():
    try:
        with open(DEVICE_FILE, "r") as f:
            data = json.load(f)
        return [dev["name"] for dev in data["supported_devices"]]
    except Exception:
        return ["Glorious Model O Wireless"]


def _setup_folder():
    try:
        os.makedirs(FOLDER, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating folder: {e}")
        return False


def _setup_file():
    try:
        with open(FILE, "w") as f:
            for name in _load_device_names():
                f.write(f"[{name}]\n")
                f.write(f"MatchName=*{name}*\n")
                f.write("ModelBouncingKeys=1\n\n")
        return True
    except Exception as e:
        print(f"Error creating file: {e}")
        return False


def setup():
    if not _setup_folder():
        print("Error creating folder!")
        return False

    if not _setup_file():
        print("Error creating file!")
        return False

    return True


print(setup())
