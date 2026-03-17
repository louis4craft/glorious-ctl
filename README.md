# glorious-ctl

A Linux control panel for Glorious wireless mice. Set RGB effects, debounce time, and check battery — no official software needed.

![Platform](https://img.shields.io/badge/platform-Linux-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Features

- **RGB Lighting** — Glorious, Cycle, Pulse, Solid, Pulse One, Tail, Rave, Wave, Off
- **Color Picker** — inline RGB picker with live preview and hex code
- **Debounce** — adjustable click debounce time (0–32 ms) per profile
- **Battery** — read battery level and charging status, auto-refresh
- **3 Profiles** — switch between profiles 1–3
- **Log Panel** — live log of all actions and errors at the bottom
- **One-time setup** — first launch guides you through permissions, never needed again

---

## Supported Mice

| Mouse | VID | PID |
|-------|-----|-----|
| Glorious Model O Wireless | `258a` | `2022` |
| Glorious Model O 2 Wireless | `258a` | `2033` |
| Glorious Model D Wireless | `258a` | `2011` |
| Glorious Model D 2 PRO 4K/8KHz Edition | `258a` | `2036` |
| Glorious Model D 2 PRO (dongle) | `258a` | `2034` |
| Glorious Model D 2 PRO (wired/direct) | `258a` | `201a` |
| Glorious Model I | `22d4` | `1503` |

> Don't see your mouse? Open an issue with the output of `lsusb` and I'll add it.

---

## Download

Grab the latest AppImage from the [Releases](../../releases) page.

```bash
chmod +x glorious-ctl-x86_64.AppImage
./glorious-ctl-x86_64.AppImage
```

---

## First Launch — Permissions

On first launch, if the app can't access the mouse, it shows a dialog with a command to copy and run once in a terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/louis4craft/glorious-ctl/refs/heads/main/setup_permissions.sh | sudo bash
```

Then **log out and back in** — the app will work without sudo from then on, permanently.

**What this does:**
- Writes a udev rule that gives your user access to the mouse's HID device whenever it's plugged in
- Adds you to the `plugdev` group
- This survives reboots and system updates

---

## Running from Source

```bash
# Clone
git clone https://github.com/louis4craft/glorious-ctl
cd glorious-ctl

# Install dependencies
pip install PySide6 hid

# Run (needs sudo first time, or after udev rule is set: without sudo)
sudo python3 mouse_gui.py
```

Both `mouse_gui.py` and `mouse.py` must be in the same folder.

## How it Works

The app communicates directly with the mouse over HID (Human Interface Device) using raw feature reports — the same protocol the official Windows software uses. No kernel module or driver needed.

The `mouse.py` backend sends byte buffers to the mouse's HID endpoint to control lighting profiles, debounce timing, and read battery status.

---

## Troubleshooting

**"No module named hid"**
```bash
pip install hid
# Also make sure hidapi is installed system-wide:
sudo apt install libhidapi-hidraw0   # Debian/Ubuntu
sudo pacman -S hidapi                # Arch
```

**Mouse not detected**
```bash
# Check if Linux sees it
lsusb | grep -i glorious

# Check HID device permissions
ls -la /dev/hidraw*
```

**App opens but can't send commands**
Make sure you've run the udev setup command and logged out/in afterwards. You can verify:
```bash
# Should show plugdev in your groups
groups $USER

# Rule should exist
cat /etc/udev/rules.d/99-glorious-mouse.rules
```

---

## License

MIT
