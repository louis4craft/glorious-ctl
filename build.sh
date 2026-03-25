#!/usr/bin/env bash
set -e

# ══════════════════════════════════════════════════════════════════════════════
# Glorious Model O — AppImage Builder & udev Setup
# Usage: chmod +x build.sh && ./build.sh
# ══════════════════════════════════════════════════════════════════════════════

ACCENT="\033[0;36m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
RESET="\033[0m"
BOLD="\033[1m"

log()  { echo -e "${ACCENT}[•]${RESET} $1"; }
ok()   { echo -e "${GREEN}[✓]${RESET} $1"; }
warn() { echo -e "${YELLOW}[⚠]${RESET} $1"; }
fail() { echo -e "${RED}[✗]${RESET} $1"; exit 1; }

echo -e "\n${BOLD}  Glorious Model O — Build & Setup Script${RESET}"
echo -e "  ─────────────────────────────────────────\n"

# ── Sanity checks ─────────────────────────────────────────────────────────────
[[ "$OSTYPE" != "linux"* ]] && fail "This script only runs on Linux."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GUI="$SCRIPT_DIR/mouse_gui.py"
BACKEND="$SCRIPT_DIR/mouse.py"
DEVICES_JSON="$SCRIPT_DIR/devices.json"

SETUP="$SCRIPT_DIR/setup.py"
[[ -f "$GUI" ]]     || fail "mouse_gui.py not found in $SCRIPT_DIR"
[[ -f "$BACKEND" ]] || fail "mouse.py not found in $SCRIPT_DIR"
[[ -f "$SETUP" ]]   || fail "setup.py not found in $SCRIPT_DIR"
[[ -f "$SCRIPT_DIR/setup_permissions.sh" ]] || fail "setup_permissions.sh not found in $SCRIPT_DIR"
[[ -f "$DEVICES_JSON" ]] || fail "devices.json not found in $SCRIPT_DIR"

# ── Step 1: Python & pip ──────────────────────────────────────────────────────
log "Checking Python..."
command -v python3 &>/dev/null || fail "python3 not found. Install it with: sudo apt install python3"
PYTHON=$(command -v python3)
ok "Python: $($PYTHON --version)"

log "Checking pip..."
command -v pip3 &>/dev/null || fail "pip3 not found. Install it with: sudo apt install python3-pip"
ok "pip found"

# ── Step 2: Install Python dependencies ──────────────────────────────────────
log "Installing Python dependencies (PySide6, hid, pyinstaller)..."
pip3 install --quiet PySide6 hid pyinstaller
ok "Python packages installed"

# ── Step 3: Download appimagetool ─────────────────────────────────────────────
APPIMAGETOOL="$SCRIPT_DIR/appimagetool-x86_64.AppImage"
if [[ ! -f "$APPIMAGETOOL" ]]; then
    log "Downloading appimagetool..."
    wget -q --show-progress \
        "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage" \
        -O "$APPIMAGETOOL"
    chmod +x "$APPIMAGETOOL"
    ok "appimagetool downloaded"
else
    ok "appimagetool already present, skipping download"
fi

# ── Step 4: PyInstaller bundle ────────────────────────────────────────────────
log "Bundling app with PyInstaller..."
cd "$SCRIPT_DIR"

pyinstaller \
    --onefile \
    --windowed \
    --name "mouse-control" \
    --add-data "$BACKEND:." \
    --add-data "$SETUP:." \
    --add-data "$DEVICES_JSON:." \
    --add-data "$SCRIPT_DIR/setup_permissions.sh:." \
    --hidden-import hid \
    --collect-all hid \
    --noconfirm \
    --clean \
    "$GUI" \
    > /dev/null 2>&1

[[ -f "$SCRIPT_DIR/dist/mouse-control" ]] || fail "PyInstaller build failed. Run manually to see errors: pyinstaller --onefile --windowed mouse_gui.py"
ok "PyInstaller build successful"

# ── Step 5: AppDir structure ──────────────────────────────────────────────────
log "Creating AppDir structure..."
APPDIR="$SCRIPT_DIR/MouseControl.AppDir"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"

cp "$SCRIPT_DIR/dist/mouse-control" "$APPDIR/usr/bin/mouse-control"
chmod +x "$APPDIR/usr/bin/mouse-control"

# Desktop entry
cat > "$APPDIR/usr/share/applications/mouse-control.desktop" << 'EOF'
[Desktop Entry]
Name=Mouse Control
Comment=Glorious Model O Wireless Control Panel
Exec=mouse-control
Icon=mouse-control
Type=Application
Categories=Utility;HardwareSettings;
Terminal=false
EOF

cp "$APPDIR/usr/share/applications/mouse-control.desktop" "$APPDIR/"

# Generate a simple SVG icon (no external dependency)
cat > "$APPDIR/mouse-control.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
  <rect width="256" height="256" rx="48" fill="#13141A"/>
  <rect x="88" y="48" width="80" height="120" rx="40" fill="none" stroke="#00E5C8" stroke-width="10"/>
  <line x1="128" y1="48" x2="128" y2="108" stroke="#00E5C8" stroke-width="10"/>
  <circle cx="128" cy="130" r="10" fill="#00E5C8"/>
  <line x1="128" y1="190" x2="128" y2="210" stroke="#00E5C8" stroke-width="6" stroke-linecap="round"/>
  <line x1="108" y1="210" x2="148" y2="210" stroke="#00E5C8" stroke-width="6" stroke-linecap="round"/>
</svg>
EOF

# Convert SVG to PNG if rsvg-convert or ImageMagick is available, else copy SVG
ICON_PNG="$APPDIR/usr/share/icons/hicolor/256x256/apps/mouse-control.png"
if command -v rsvg-convert &>/dev/null; then
    rsvg-convert -w 256 -h 256 "$APPDIR/mouse-control.svg" -o "$ICON_PNG"
    cp "$ICON_PNG" "$APPDIR/mouse-control.png"
    ok "Icon generated (rsvg-convert)"
elif command -v convert &>/dev/null; then
    convert -background none "$APPDIR/mouse-control.svg" -resize 256x256 "$ICON_PNG" 2>/dev/null
    cp "$ICON_PNG" "$APPDIR/mouse-control.png"
    ok "Icon generated (ImageMagick)"
else
    # Fallback: use SVG directly (some AppImage tools accept it)
    cp "$APPDIR/mouse-control.svg" "$APPDIR/mouse-control.png"
    warn "No image converter found — using SVG as icon fallback (install librsvg2-bin for a proper PNG)"
fi

# AppRun entrypoint
cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE="${SELF%/*}"
exec "$HERE/usr/bin/mouse-control" "$@"
EOF
chmod +x "$APPDIR/AppRun"

ok "AppDir ready"

# ── Step 6: Build AppImage ────────────────────────────────────────────────────
log "Building AppImage..."
OUTPUT="$SCRIPT_DIR/MouseControl.AppImage"

ARCH=x86_64 "$APPIMAGETOOL" "$APPDIR" "$OUTPUT" > /dev/null 2>&1

[[ -f "$OUTPUT" ]] || fail "appimagetool failed to create the AppImage."
chmod +x "$OUTPUT"
ok "AppImage built: $OUTPUT"

# ── Step 7: udev rule ─────────────────────────────────────────────────────────
UDEV_RULE="/etc/udev/rules.d/99-glorious-mouse.rules"
RULE_CONTENT='SUBSYSTEM=="hidraw", ATTRS{idVendor}=="258a", ATTRS{idProduct}=="2022", MODE="0666", GROUP="plugdev"'

log "Setting up udev rule for HID access (requires sudo)..."

if [[ -f "$UDEV_RULE" ]] && grep -q "258a" "$UDEV_RULE" 2>/dev/null; then
    ok "udev rule already exists, skipping"
else
    echo "$RULE_CONTENT" | sudo tee "$UDEV_RULE" > /dev/null
    ok "udev rule written to $UDEV_RULE"
fi

log "Reloading udev rules..."
sudo udevadm control --reload-rules
sudo udevadm trigger
ok "udev rules reloaded"

# ── Step 8: libinput quirks (setup.py) ───────────────────────────────────────
log "Running libinput quirks setup (requires sudo)..."
if sudo python3 "$SETUP"; then
    ok "libinput quirks configured (/etc/libinput/local-overrides.quirks)"
else
    warn "setup.py failed — debounce fix via libinput not applied (non-critical)"
fi

# ── Step 9: plugdev group ─────────────────────────────────────────────────────
CURRENT_USER="${SUDO_USER:-$USER}"
if groups "$CURRENT_USER" | grep -q "plugdev"; then
    ok "User '$CURRENT_USER' is already in plugdev group"
else
    log "Adding '$CURRENT_USER' to plugdev group..."
    sudo usermod -aG plugdev "$CURRENT_USER"
    ok "User added to plugdev"
    warn "You need to log out and back in for the group change to take effect."
fi

# ── Cleanup ───────────────────────────────────────────────────────────────────
log "Cleaning up build artifacts..."
rm -rf "$SCRIPT_DIR/dist" "$SCRIPT_DIR/build" "$SCRIPT_DIR/__pycache__" "$SCRIPT_DIR/mouse-control.spec"
ok "Cleaned up"

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}  All done!${RESET}"
echo -e "  AppImage: ${BOLD}$OUTPUT${RESET}"
echo -e "  Run with: ${ACCENT}./MouseControl.AppImage${RESET}"
echo -e "  No sudo needed after re-login.\n"
