import os

FOLDER = "/etc/libinput"
FILE = "/etc/libinput/local-overrides.quirks"


def _setup_folder():
    try:
        os.makedirs(FOLDER, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating folder: {e}")
        return False


def _setup_file():
    if os.path.exists(FILE):
        return True

    try:
        with open(FILE, "w") as f:
            f.write("[Glorious Model O Wireless]\n")
            f.write("MatchName=*Glorious Model O Wireless*\n")
            f.write("ModelBouncingKeys=1\n")
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