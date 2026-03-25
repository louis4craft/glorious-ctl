#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════════════════
# glorious-ctl — One-time permission setup
# Run once with: sudo bash setup_permissions.sh
# ══════════════════════════════════════════════════════════════════════════════
set -e

GREEN="\033[0;32m"
CYAN="\033[0;36m"
YELLOW="\033[1;33m"
RESET="\033[0m"

ok()   { echo -e "${GREEN}[✓]${RESET} $1"; }
log()  { echo -e "${CYAN}[•]${RESET} $1"; }
warn() { echo -e "${YELLOW}[⚠]${RESET} $1"; }

echo -e "\n  glorious-ctl — Permission Setup\n"

# ── 1. udev rules (HID access without sudo) ───────────────────────────────────
log "Writing udev rules..."

cat > /etc/udev/rules.d/99-glorious-mouse.rules << 'EOF'
# Glorious Model O Wireless
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="258a", ATTRS{idProduct}=="2022", MODE="0666", GROUP="plugdev"
# Glorious Model O 2 Wireless
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="258a", ATTRS{idProduct}=="2033", MODE="0666", GROUP="plugdev"
# Glorious Model D Wireless
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="258a", ATTRS{idProduct}=="2011", MODE="0666", GROUP="plugdev"
# Glorious Model D 2 PRO 4K/8KHz Edition
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="258a", ATTRS{idProduct}=="2036", MODE="0666", GROUP="plugdev"
# Glorious Model D 2 PRO (dongle)
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="258a", ATTRS{idProduct}=="2034", MODE="0666", GROUP="plugdev"
# Glorious Model D 2 PRO (wired/direct)
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="258a", ATTRS{idProduct}=="201a", MODE="0666", GROUP="plugdev"
# Glorious Model I (Laview Technology OEM)
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="22d4", ATTRS{idProduct}=="1503", MODE="0666", GROUP="plugdev"
# Glorious Model I 2 Wireless (Pixart Imaging OEM)
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="093a", ATTRS{idProduct}=="821a", MODE="0666", GROUP="plugdev"
# Glorious Model O V2 Wired (VID 320f)
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="320f", ATTRS{idProduct}=="823a", MODE="0666", GROUP="plugdev"
# Glorious Model D- Wireless
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="258a", ATTRS{idProduct}=="2025", MODE="0666", GROUP="plugdev"
EOF

udevadm control --reload-rules
udevadm trigger
ok "udev rules written and reloaded"

# ── 2. plugdev group ──────────────────────────────────────────────────────────
CURRENT_USER="${SUDO_USER:-$USER}"

# Create plugdev group if it doesn't exist (not present by default on Arch)
if ! getent group plugdev > /dev/null 2>&1; then
    log "plugdev group not found, creating it..."
    groupadd plugdev
    ok "plugdev group created"
fi

if groups "$CURRENT_USER" | grep -q "plugdev"; then
    ok "User '$CURRENT_USER' already in plugdev group"
else
    log "Adding '$CURRENT_USER' to plugdev group..."
    usermod -aG plugdev "$CURRENT_USER"
    ok "User added to plugdev group"
fi

# ── 3. libinput debounce quirks ───────────────────────────────────────────────
log "Writing libinput debounce quirks..."

mkdir -p /etc/libinput

cat > /etc/libinput/local-overrides.quirks << 'EOF'
[Glorious Model O Wireless]
MatchName=*Glorious Model O Wireless*
ModelBouncingKeys=1

[Glorious Model O 2 Wireless]
MatchName=*Glorious Model O 2 Wireless*
ModelBouncingKeys=1

[Glorious Model D Wireless]
MatchName=*Glorious Model D Wireless*
ModelBouncingKeys=1

[Glorious Model D 2 PRO 4K/8KHz Edition]
MatchName=*Glorious Model D 2 PRO 4K/8KHz Edition*
ModelBouncingKeys=1

[Glorious Model D 2 PRO]
MatchName=*Glorious Model D 2 PRO*
ModelBouncingKeys=1

[Glorious Model I]
MatchName=*Glorious Model I*
ModelBouncingKeys=1

[Glorious Model I 2 Wireless]
MatchName=*Glorious Model I 2 Wireless*
ModelBouncingKeys=1

[Glorious Model O V2 Wired]
MatchName=*Glorious Model O V2 Wired*
ModelBouncingKeys=1

[Glorious Model D- Wireless]
MatchName=*Glorious Model D- Wireless*
ModelBouncingKeys=1
EOF

ok "libinput quirks written"

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
ok "Setup complete!"
warn "Please log out and back in for the group change to take effect."
echo ""