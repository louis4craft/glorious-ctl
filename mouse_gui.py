"""
Glorious Model O Wireless — Control Panel
Requires: pip install PySide6 hid
Place this file alongside mouse.py (or adjust the import path below).
"""

import sys
import os
import importlib.util
import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QSlider, QComboBox, QSpinBox,
    QGroupBox, QGridLayout, QSizePolicy, QMessageBox, QCheckBox,
    QDialog, QDialogButtonBox, QTextEdit, QFrame, QLineEdit,
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QObject
from PySide6.QtGui import (
    QColor, QPainter, QBrush, QLinearGradient, QPalette, QTextCursor, QPen,
)

# ══════════════════════════════════════════════════════════════════════════════
# Backend import
# Works both when run as a plain .py and when frozen by PyInstaller.
# PyInstaller extracts bundled data files to sys._MEIPASS at runtime.
# ══════════════════════════════════════════════════════════════════════════════
def _find_backend() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "mouse.py"
    return Path(__file__).parent / "mouse.py"

try:
    _backend_path = _find_backend()
    spec = importlib.util.spec_from_file_location("mouse", _backend_path)
    mouse = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mouse)
    BACKEND_AVAILABLE = True
    BACKEND_ERROR = ""
except Exception as _be:
    BACKEND_AVAILABLE = False
    BACKEND_ERROR = str(_be)

# ══════════════════════════════════════════════════════════════════════════════
# Palette
# ══════════════════════════════════════════════════════════════════════════════
C_BG       = "#0B0C0E"
C_SURFACE  = "#13141A"
C_SURFACE2 = "#1C1D26"
C_BORDER   = "#2A2B38"
C_ACCENT   = "#00E5C8"
C_ACCENT2  = "#0066FF"
C_TEXT     = "#E8EAF0"
C_MUTED    = "#5A5D70"
C_SUCCESS  = "#22C55E"
C_WARNING  = "#F59E0B"
C_ERROR    = "#EF4444"

STYLESHEET = f"""
QMainWindow, QWidget {{
    background: {C_BG};
    color: {C_TEXT};
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 13px;
}}
QTabWidget::pane {{
    border: 1px solid {C_BORDER};
    border-radius: 8px;
    background: {C_SURFACE};
    margin-top: -1px;
}}
QTabBar::tab {{
    background: {C_SURFACE2};
    color: {C_MUTED};
    padding: 10px 24px;
    border: 1px solid {C_BORDER};
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
    font-size: 12px;
    letter-spacing: 1px;
    text-transform: uppercase;
}}
QTabBar::tab:selected {{
    background: {C_SURFACE};
    color: {C_ACCENT};
    border-bottom: 2px solid {C_ACCENT};
}}
QTabBar::tab:hover:!selected {{ color: {C_TEXT}; background: #1A1B24; }}
QGroupBox {{
    border: 1px solid {C_BORDER};
    border-radius: 8px;
    margin-top: 14px;
    padding: 16px 12px 12px 12px;
    background: {C_SURFACE};
    font-size: 11px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: {C_MUTED};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 8px;
    background: {C_SURFACE};
    color: {C_ACCENT};
    border-radius: 4px;
}}
QPushButton {{
    background: {C_SURFACE2};
    color: {C_TEXT};
    border: 1px solid {C_BORDER};
    border-radius: 6px;
    padding: 9px 20px;
    font-size: 12px;
    letter-spacing: 0.5px;
}}
QPushButton:hover {{ background: #22243A; border-color: {C_ACCENT}; color: {C_ACCENT}; }}
QPushButton:pressed {{ background: #0D1A28; }}
QPushButton:disabled {{ background: {C_SURFACE}; color: {C_MUTED}; border-color: {C_BORDER}; }}
QPushButton#accent {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {C_ACCENT}, stop:1 #00BFAA);
    color: #000; border: none; font-weight: bold; letter-spacing: 1px;
}}
QPushButton#accent:hover {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #33EED5, stop:1 #33CFBB);
    color: #000;
}}
QPushButton#accent:pressed {{ background: #009980; }}
QPushButton#accent:disabled {{ background: #1A3030; color: #2A5050; border: none; }}
QSlider::groove:horizontal {{ height: 4px; background: {C_BORDER}; border-radius: 2px; }}
QSlider::handle:horizontal {{
    background: {C_ACCENT}; border: none;
    width: 16px; height: 16px; margin: -6px 0; border-radius: 8px;
}}
QSlider::sub-page:horizontal {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {C_ACCENT2}, stop:1 {C_ACCENT});
    border-radius: 2px;
}}
QComboBox {{
    background: {C_SURFACE2}; border: 1px solid {C_BORDER};
    border-radius: 6px; padding: 7px 12px; color: {C_TEXT}; min-width: 140px;
}}
QComboBox:hover {{ border-color: {C_ACCENT}; }}
QComboBox::drop-down {{ border: none; width: 28px; }}
QComboBox::down-arrow {{
    width: 10px; height: 10px; image: none;
    border-left: 5px solid transparent; border-right: 5px solid transparent;
    border-top: 5px solid {C_MUTED}; margin-right: 8px;
}}
QComboBox QAbstractItemView {{
    background: {C_SURFACE2}; border: 1px solid {C_BORDER}; color: {C_TEXT};
    selection-background-color: #1A2D3A; selection-color: {C_ACCENT}; padding: 4px;
}}
QSpinBox {{
    background: {C_SURFACE2}; border: 1px solid {C_BORDER};
    border-radius: 6px; padding: 7px 10px; color: {C_TEXT}; min-width: 70px;
}}
QSpinBox:hover {{ border-color: {C_ACCENT}; }}
QSpinBox::up-button, QSpinBox::down-button {{
    background: {C_BORDER}; border: none; width: 18px; border-radius: 3px;
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {{ background: {C_ACCENT}; }}
QCheckBox {{ spacing: 8px; color: {C_TEXT}; }}
QCheckBox::indicator {{
    width: 18px; height: 18px; border: 1px solid {C_BORDER};
    border-radius: 4px; background: {C_SURFACE2};
}}
QCheckBox::indicator:checked {{ background: {C_ACCENT}; border-color: {C_ACCENT}; }}
QLabel#value {{ color: {C_ACCENT}; font-size: 13px; min-width: 30px; }}
QLabel#mono_big {{ color: {C_TEXT}; font-size: 28px; }}
QTextEdit#log {{
    background: #0D0E12; color: {C_TEXT}; border: none;
    border-top: 1px solid {C_BORDER}; font-size: 11px;
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    padding: 6px 10px;
}}
QWidget#save_bar {{ background: {C_SURFACE}; border-top: 1px solid {C_BORDER}; }}
QScrollArea {{ border: none; background: transparent; }}
QScrollBar:vertical {{ background: {C_SURFACE}; width: 6px; border-radius: 3px; }}
QScrollBar::handle:vertical {{
    background: {C_BORDER}; border-radius: 3px; min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
"""

# ══════════════════════════════════════════════════════════════════════════════
# Global Logger
# ══════════════════════════════════════════════════════════════════════════════
class _LoggerSignals(QObject):
    message = Signal(str)

_log_signals = _LoggerSignals()

def _ts() -> str:
    return datetime.datetime.now().strftime("%H:%M:%S")

def log_info(msg: str):
    _log_signals.message.emit(
        f'<span style="color:{C_MUTED}">[{_ts()}]</span> '
        f'<span style="color:{C_TEXT}">{msg}</span>'
    )

def log_ok(msg: str):
    _log_signals.message.emit(
        f'<span style="color:{C_MUTED}">[{_ts()}]</span> '
        f'<span style="color:{C_SUCCESS}">&#10003; {msg}</span>'
    )

def log_warn(msg: str):
    _log_signals.message.emit(
        f'<span style="color:{C_MUTED}">[{_ts()}]</span> '
        f'<span style="color:{C_WARNING}">&#9888; {msg}</span>'
    )

def log_err(msg: str):
    _log_signals.message.emit(
        f'<span style="color:{C_MUTED}">[{_ts()}]</span> '
        f'<span style="color:{C_ERROR}">&#10007; {msg}</span>'
    )

# ══════════════════════════════════════════════════════════════════════════════
# Worker thread
# ══════════════════════════════════════════════════════════════════════════════
class Worker(QThread):
    done = Signal(bool, str)

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self._fn = fn
        self._args = args
        self._kwargs = kwargs

    def run(self):
        try:
            result = self._fn(*self._args, **self._kwargs)
            self.done.emit(True, str(result) if result is not None else "OK")
        except Exception as e:
            self.done.emit(False, str(e))

# ══════════════════════════════════════════════════════════════════════════════
# RGB Picker Dialog  (for multi-color swatches)
# ══════════════════════════════════════════════════════════════════════════════
class RGBPickerDialog(QDialog):
    def __init__(self, initial: QColor, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pick Color")
        self.setFixedSize(360, 270)
        self._color = QColor(initial)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 16)

        self._preview = QLabel()
        self._preview.setFixedHeight(52)
        r, g, b = initial.red(), initial.green(), initial.blue()
        self._preview.setStyleSheet(f"border-radius: 8px; background: rgb({r},{g},{b});")
        layout.addWidget(self._preview)

        self._hex_lbl = QLabel(f"#{r:02X}{g:02X}{b:02X}")
        self._hex_lbl.setAlignment(Qt.AlignCenter)
        self._hex_lbl.setStyleSheet(f"color: {C_MUTED}; font-size: 12px; letter-spacing: 2px;")
        layout.addWidget(self._hex_lbl)

        grid = QGridLayout()
        grid.setSpacing(10)
        self._sliders: dict[str, QSlider] = {}
        self._val_lbls: dict[str, QLabel] = {}
        for i, (ch, label, col) in enumerate([
            ("R","RED",C_ERROR), ("G","GREEN",C_SUCCESS), ("B","BLUE",C_ACCENT2)
        ]):
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color:{col}; font-size:11px; letter-spacing:1px; min-width:48px;")
            sl = QSlider(Qt.Horizontal)
            sl.setRange(0, 255)
            sl.setValue(getattr(initial, ch.lower())())
            val = QLabel(str(sl.value()))
            val.setObjectName("value")
            val.setFixedWidth(36)
            val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            sl.valueChanged.connect(self._on_change)
            self._sliders[ch] = sl
            self._val_lbls[ch] = val
            grid.addWidget(lbl, i, 0)
            grid.addWidget(sl,  i, 1)
            grid.addWidget(val, i, 2)
        layout.addLayout(grid)

        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        layout.addWidget(bb)

    def _on_change(self):
        r = self._sliders["R"].value()
        g = self._sliders["G"].value()
        b = self._sliders["B"].value()
        for ch, v in zip(["R","G","B"], [r,g,b]):
            self._val_lbls[ch].setText(str(v))
        self._color = QColor(r, g, b)
        self._preview.setStyleSheet(f"border-radius: 8px; background: rgb({r},{g},{b});")
        self._hex_lbl.setText(f"#{r:02X}{g:02X}{b:02X}")

    def color(self) -> QColor:
        return self._color

# ══════════════════════════════════════════════════════════════════════════════
# Color Swatch button
# ══════════════════════════════════════════════════════════════════════════════
class ColorSwatch(QPushButton):
    def __init__(self, color: QColor = QColor(255, 0, 0), parent=None):
        super().__init__(parent)
        self._color = color
        self.setFixedSize(44, 44)
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(self._open_picker)
        self._update_style()

    def _update_style(self):
        r, g, b = self._color.red(), self._color.green(), self._color.blue()
        lum = 0.299*r + 0.587*g + 0.114*b
        txt = "#000" if lum > 140 else "#fff"
        self.setStyleSheet(
            f"QPushButton {{ background: rgb({r},{g},{b}); border-radius: 6px;"
            f"border: 2px solid rgba(255,255,255,0.12); color:{txt}; font-size:9px; }}"
            f"QPushButton:hover {{ border: 2px solid {C_ACCENT}; }}"
        )
        self.setToolTip(f"#{r:02X}{g:02X}{b:02X}  — click to change")

    def _open_picker(self):
        dlg = RGBPickerDialog(self._color, self)
        if dlg.exec():
            self._color = dlg.color()
            self._update_style()

    def color(self) -> QColor:  return self._color
    def set_color(self, c: QColor): self._color = c; self._update_style()

# ══════════════════════════════════════════════════════════════════════════════
# Inline Color Picker  (used for Solid effect)
# ══════════════════════════════════════════════════════════════════════════════
class InlineColorPicker(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self._preview = QWidget()
        self._preview.setFixedHeight(48)
        self._preview.setStyleSheet("border-radius: 8px; background: rgb(255,0,0);")
        layout.addWidget(self._preview)

        self._hex_lbl = QLabel("#FF0000")
        self._hex_lbl.setAlignment(Qt.AlignCenter)
        self._hex_lbl.setStyleSheet(f"color: {C_MUTED}; font-size: 11px; letter-spacing: 2px;")
        layout.addWidget(self._hex_lbl)

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setContentsMargins(0, 0, 0, 0)
        self._sliders: dict[str, QSlider] = {}
        self._vals:    dict[str, QLabel]  = {}

        for i, (ch, label, col, default) in enumerate([
            ("R", "RED",   C_ERROR,   255),
            ("G", "GREEN", C_SUCCESS, 0),
            ("B", "BLUE",  C_ACCENT2, 0),
        ]):
            lbl = QLabel(label)
            lbl.setStyleSheet(
                f"color: {col}; font-size: 11px; letter-spacing:1px; min-width:50px;"
            )
            sl = QSlider(Qt.Horizontal)
            sl.setRange(0, 255)
            sl.setValue(default)
            val = QLabel(str(default))
            val.setObjectName("value")
            val.setFixedWidth(36)
            val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            sl.valueChanged.connect(self._on_change)
            self._sliders[ch] = sl
            self._vals[ch] = val
            grid.addWidget(lbl, i, 0)
            grid.addWidget(sl,  i, 1)
            grid.addWidget(val, i, 2)

        layout.addLayout(grid)
        self._on_change()

    def _on_change(self):
        r = self._sliders["R"].value()
        g = self._sliders["G"].value()
        b = self._sliders["B"].value()
        for ch, v in zip(["R","G","B"], [r,g,b]):
            self._vals[ch].setText(str(v))
        self._preview.setStyleSheet(f"border-radius: 8px; background: rgb({r},{g},{b});")
        self._hex_lbl.setText(f"#{r:02X}{g:02X}{b:02X}")

    def color(self) -> QColor:
        return QColor(
            self._sliders["R"].value(),
            self._sliders["G"].value(),
            self._sliders["B"].value(),
        )

    def set_color(self, c: QColor):
        self._sliders["R"].setValue(c.red())
        self._sliders["G"].setValue(c.green())
        self._sliders["B"].setValue(c.blue())

# ══════════════════════════════════════════════════════════════════════════════
# Lighting Tab
# ══════════════════════════════════════════════════════════════════════════════
EFFECTS      = ["Glorious","Cycle","Pulse","Solid","Pulse One","Tail","Rave","Wave","Off"]
RATE_EFFECTS = {"Glorious","Cycle","Pulse","Pulse One","Tail","Rave","Wave"}
COLOR_COUNT  = {"Pulse One": 1, "Pulse": 6, "Rave": 2}   # Solid uses inline picker

class LightingTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: transparent;")
        self._worker = None

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(14)

        # Effect + Profile
        eff_box = QGroupBox("Effect")
        eff_l = QHBoxLayout(eff_box)
        eff_l.addWidget(QLabel("Mode"))
        self.effect_combo = QComboBox()
        self.effect_combo.addItems(EFFECTS)
        self.effect_combo.currentIndexChanged.connect(self._on_effect_change)
        eff_l.addWidget(self.effect_combo)
        eff_l.addSpacing(20)
        eff_l.addWidget(QLabel("Profile"))
        self.profile_spin = QSpinBox()
        self.profile_spin.setRange(1, 3)
        eff_l.addWidget(self.profile_spin)
        eff_l.addStretch()
        root.addWidget(eff_box)

        # Rate
        self.rate_box = QGroupBox("Rate  (0 = slow  \u2192  100 = fast)")
        rate_l = QHBoxLayout(self.rate_box)
        self.rate_slider = QSlider(Qt.Horizontal)
        self.rate_slider.setRange(0, 100)
        self.rate_slider.setValue(40)
        self.rate_val = QLabel("40")
        self.rate_val.setObjectName("value")
        self.rate_val.setFixedWidth(32)
        self.rate_slider.valueChanged.connect(lambda v: self.rate_val.setText(str(v)))
        rate_l.addWidget(self.rate_slider)
        rate_l.addWidget(self.rate_val)
        root.addWidget(self.rate_box)

        # Solid color picker
        self.solid_box = QGroupBox("Color")
        solid_l = QVBoxLayout(self.solid_box)
        self.inline_picker = InlineColorPicker()
        solid_l.addWidget(self.inline_picker)
        root.addWidget(self.solid_box)

        # Multi-color swatches
        self.color_box = QGroupBox("Colors  (click to edit)")
        self.color_inner = QHBoxLayout(self.color_box)
        self.color_inner.setSpacing(10)
        self._swatches: list[ColorSwatch] = []
        root.addWidget(self.color_box)

        root.addStretch()
        self._on_effect_change(0)

    def _on_effect_change(self, _=None):
        name = self.effect_combo.currentText()
        self.rate_box.setVisible(name in RATE_EFFECTS)
        self.solid_box.setVisible(name == "Solid")
        n = COLOR_COUNT.get(name, 0)
        self.color_box.setVisible(n > 0)

        for sw in self._swatches:
            sw.deleteLater()
        self._swatches.clear()

        defaults = [
            QColor(255,0,0), QColor(0,255,0), QColor(0,0,255),
            QColor(255,255,0), QColor(255,0,255), QColor(0,255,255),
        ]
        for i in range(n):
            sw = ColorSwatch(defaults[i % len(defaults)])
            self._swatches.append(sw)
            self.color_inner.addWidget(sw)
        if n > 0:
            self.color_inner.addStretch()

    def build_effect(self):
        if not BACKEND_AVAILABLE:
            return None
        name  = self.effect_combo.currentText()
        rate  = self.rate_slider.value()
        ic    = self.inline_picker.color()
        solid = mouse.Color(ic.red(), ic.green(), ic.blue())
        colors = [
            mouse.Color(sw.color().red(), sw.color().green(), sw.color().blue())
            for sw in self._swatches
        ]
        m = mouse.Effect
        match name:
            case "Glorious":  return m.Glorious(rate)
            case "Cycle":     return m.Cycle(rate)
            case "Pulse":     return m.Pulse(rate, colors)
            case "Solid":     return m.Solid(solid)
            case "Pulse One": return m.PulseOne(rate, colors[0] if colors else solid)
            case "Tail":      return m.Tail(rate)
            case "Rave":      return m.Rave(rate, colors)
            case "Wave":      return m.Wave(rate)
            case "Off":       return m.Off()
        return None

    def trigger_apply(self):
        if not BACKEND_AVAILABLE:
            log_err(f"Backend not available: {BACKEND_ERROR}")
            return
        effect  = self.build_effect()
        profile = self.profile_spin.value()
        name    = self.effect_combo.currentText()
        log_info(f"Sending effect '{name}' (profile {profile})...")
        self._worker = Worker(mouse.set_rgb, profile=profile, effect=effect)
        self._worker.done.connect(self._on_done)
        self._worker.start()

    def _on_done(self, ok: bool, msg: str):
        name = self.effect_combo.currentText()
        if ok:
            log_ok(f"Effect '{name}' applied successfully")
        else:
            log_err(f"Failed to apply effect '{name}': {msg}")

# ══════════════════════════════════════════════════════════════════════════════
# Settings Tab
# ══════════════════════════════════════════════════════════════════════════════
class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: transparent;")
        self._worker = None

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(14)

        deb_box = QGroupBox("Click Debounce")
        deb_l = QVBoxLayout(deb_box)
        deb_l.setSpacing(12)

        info = QLabel(
            "Debounce prevents unintentional double-clicks.\n"
            "Low = faster response  |  High = more protection."
        )
        info.setStyleSheet(f"color: {C_MUTED}; font-size: 12px;")
        info.setWordWrap(True)
        deb_l.addWidget(info)

        row = QHBoxLayout()
        row.addWidget(QLabel("Debounce"))
        self.deb_slider = QSlider(Qt.Horizontal)
        self.deb_slider.setRange(0, 32)
        self.deb_slider.setValue(8)
        self.deb_val = QLabel("8 ms")
        self.deb_val.setObjectName("value")
        self.deb_val.setFixedWidth(56)
        self.deb_slider.valueChanged.connect(lambda v: self.deb_val.setText(f"{v} ms"))
        row.addWidget(self.deb_slider)
        row.addWidget(self.deb_val)
        deb_l.addLayout(row)

        prof_row = QHBoxLayout()
        prof_row.addWidget(QLabel("Profile"))
        self.deb_profile = QSpinBox()
        self.deb_profile.setRange(1, 3)
        prof_row.addWidget(self.deb_profile)
        prof_row.addStretch()
        deb_l.addLayout(prof_row)
        root.addWidget(deb_box)

        dev_box = QGroupBox("Detected Device")
        dev_l = QVBoxLayout(dev_box)
        self._device_lbl = QLabel("Checking...")
        self._device_lbl.setWordWrap(True)
        dev_l.addWidget(self._device_lbl)
        root.addWidget(dev_box)

        root.addStretch()
        self._detect_device()

    def _detect_device(self):
        if not BACKEND_AVAILABLE:
            self._device_lbl.setText(f"Backend error: {BACKEND_ERROR}")
            self._device_lbl.setStyleSheet(f"color: {C_ERROR}; font-size:12px;")
            log_err(f"Backend could not be loaded: {BACKEND_ERROR}")
            return
        try:
            result = mouse.check_for_supported_mice()
            if result:
                self._device_lbl.setText(f"{result.strip()}")
                self._device_lbl.setStyleSheet(f"color: {C_SUCCESS}; font-size:12px;")
                log_ok(f"Device found: {result.strip()}")
            else:
                self._device_lbl.setText("No supported device found via lsusb.")
                self._device_lbl.setStyleSheet(f"color: {C_WARNING}; font-size:12px;")
                log_warn("No supported device detected via lsusb")
        except Exception as e:
            self._device_lbl.setText(f"Error: {e}")
            self._device_lbl.setStyleSheet(f"color: {C_ERROR}; font-size:12px;")
            log_err(f"lsusb check failed: {e}")

    def trigger_apply(self):
        if not BACKEND_AVAILABLE:
            log_err(f"Backend not available: {BACKEND_ERROR}")
            return
        ms      = self.deb_slider.value()
        profile = self.deb_profile.value()
        log_info(f"Setting debounce to {ms} ms (profile {profile})...")
        self._worker = Worker(mouse.set_debounce_time, ms, profile)
        self._worker.done.connect(self._on_done)
        self._worker.start()

    def _on_done(self, ok: bool, msg: str):
        ms = self.deb_slider.value()
        if ok:
            log_ok(f"Debounce set to {ms} ms")
        else:
            log_err(f"Debounce failed: {msg}")

# ══════════════════════════════════════════════════════════════════════════════
# Battery Tab
# ══════════════════════════════════════════════════════════════════════════════
class BatteryBar(QWidget):
    def __init__(self):
        super().__init__()
        self._value = 0
        self.setFixedHeight(28)

    def setValue(self, v: int):
        self._value = max(0, min(100, v))
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(C_BORDER))
        p.drawRoundedRect(0, 0, w-16, h, h//2, h//2)
        p.drawRoundedRect(w-12, h//4, 12, h//2, 4, 4)
        if self._value > 0:
            fill_w = int((w-20) * self._value / 100)
            color  = QColor(C_ACCENT if self._value > 60 else C_WARNING if self._value > 25 else C_ERROR)
            grad   = QLinearGradient(0, 0, fill_w, 0)
            grad.setColorAt(0.0, color.darker(120))
            grad.setColorAt(1.0, color)
            p.setBrush(QBrush(grad))
            p.drawRoundedRect(2, 2, fill_w, h-4, (h-4)//2, (h-4)//2)
        p.end()


class BatteryTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: transparent;")
        self._worker = None

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(14)

        status_box = QGroupBox("Battery Status")
        sl = QVBoxLayout(status_box)
        sl.setSpacing(12)
        self._battery_lbl = QLabel("--")
        self._battery_lbl.setObjectName("mono_big")
        self._battery_lbl.setAlignment(Qt.AlignCenter)
        sl.addWidget(self._battery_lbl)
        self._bar = BatteryBar()
        sl.addWidget(self._bar)
        self._detail_lbl = QLabel("")
        self._detail_lbl.setAlignment(Qt.AlignCenter)
        self._detail_lbl.setStyleSheet(f"color: {C_MUTED}; font-size:12px;")
        sl.addWidget(self._detail_lbl)
        root.addWidget(status_box)

        ctrl_box = QGroupBox("Options")
        cl = QHBoxLayout(ctrl_box)
        self.wired_cb = QCheckBox("Wired mode")
        self.wired_cb.setToolTip(
            "Enable when connected via USB cable.\nShows charging status instead of battery %."
        )
        cl.addWidget(self.wired_cb)
        cl.addStretch()
        root.addWidget(ctrl_box)

        auto_row = QHBoxLayout()
        self._auto_cb = QCheckBox("Auto-refresh every 30 s")
        self._auto_cb.stateChanged.connect(self._toggle_auto)
        auto_row.addWidget(self._auto_cb)
        auto_row.addStretch()
        root.addLayout(auto_row)
        root.addStretch()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.trigger_apply)

    def _toggle_auto(self, state):
        if state == Qt.Checked.value:
            self._timer.start(30_000)
            log_info("Auto-refresh enabled (30 s)")
        else:
            self._timer.stop()
            log_info("Auto-refresh disabled")

    def trigger_apply(self):
        if not BACKEND_AVAILABLE:
            log_err(f"Backend not available: {BACKEND_ERROR}")
            return
        self._battery_lbl.setText("...")
        self._detail_lbl.setText("Reading device...")
        log_info("Reading battery status...")
        wired = self.wired_cb.isChecked()
        self._worker = Worker(mouse.get_battery_status, wired)
        self._worker.done.connect(self._on_done)
        self._worker.start()

    def _on_done(self, ok: bool, msg: str):
        if ok:
            self._battery_lbl.setText(msg)
            try:
                pct = int(msg.replace("%","").split()[0])
                self._bar.setValue(pct)
                log_ok(f"Battery level: {msg}")
            except Exception:
                self._bar.setValue(0)
                log_info(f"Battery status: {msg}")
            self._detail_lbl.setText("Last read: just now")
        else:
            self._battery_lbl.setText("Error")
            self._bar.setValue(0)
            self._detail_lbl.setText(f"Error: {msg}")
            log_err(f"Failed to read battery: {msg}")

# ══════════════════════════════════════════════════════════════════════════════
# Startup Check Dialog
# ══════════════════════════════════════════════════════════════════════════════
class StartupCheckDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Geraetepruefung")
        self.setFixedSize(480, 270)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 24)
        layout.setSpacing(14)

        title_row = QHBoxLayout()
        icon = QLabel("◈")
        icon.setStyleSheet(f"color: {C_ACCENT}; font-size: 26px;")
        title_row.addWidget(icon)
        title = QLabel("GLORIOUS MODEL O")
        title.setStyleSheet(
            f"color: {C_TEXT}; font-size: 16px; letter-spacing: 3px; font-weight: bold; margin-left:6px;"
        )
        title_row.addWidget(title)
        title_row.addStretch()
        layout.addLayout(title_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color: {C_BORDER};")
        layout.addWidget(sep)

        self._status_lbl = QLabel("Pruefe Verbindung...")
        self._status_lbl.setStyleSheet(f"color: {C_MUTED}; font-size: 13px;")
        self._status_lbl.setWordWrap(True)
        layout.addWidget(self._status_lbl)

        self._detail_lbl = QLabel("")
        self._detail_lbl.setStyleSheet(f"color: {C_MUTED}; font-size: 11px;")
        self._detail_lbl.setWordWrap(True)
        layout.addWidget(self._detail_lbl)

        layout.addStretch()

        btn_row = QHBoxLayout()
        self._abort_btn = QPushButton("Beenden")
        self._abort_btn.clicked.connect(self.reject)
        self._ok_btn = QPushButton("  Oeffnen  →")
        self._ok_btn.setObjectName("accent")
        self._ok_btn.setVisible(False)
        self._ok_btn.clicked.connect(self.accept)
        btn_row.addWidget(self._abort_btn)
        btn_row.addStretch()
        btn_row.addWidget(self._ok_btn)
        layout.addLayout(btn_row)

        QTimer.singleShot(80, self._run_check)

    def _run_check(self):
        if not BACKEND_AVAILABLE:
            self._status_lbl.setText("Backend konnte nicht geladen werden")
            self._status_lbl.setStyleSheet(f"color: {C_ERROR}; font-size: 13px;")
            self._detail_lbl.setText(
                f"Fehler: {BACKEND_ERROR}\n\n"
                "Stelle sicher, dass mouse.py im gleichen Ordner liegt "
                "und 'pip install hid' ausgefuehrt wurde."
            )
            # only abort available, no "open anyway"
            return
        try:
            found = mouse.check_for_supported_mice()
            if found:
                self._status_lbl.setText("Maus erkannt!")
                self._status_lbl.setStyleSheet(
                    f"color: {C_SUCCESS}; font-size: 14px; font-weight: bold;"
                )
                self._detail_lbl.setText(found.strip())
                self._ok_btn.setVisible(True)
            else:
                self._status_lbl.setText("Keine unterstuetzte Maus gefunden")
                self._status_lbl.setStyleSheet(f"color: {C_ERROR}; font-size: 13px;")
                self._detail_lbl.setText(
                    "Glorious Model O Wireless nicht ueber lsusb erkannt.\n"
                    "Stelle sicher, dass die Maus verbunden und eingeschaltet ist."
                )
                # no open button — must connect mouse first
        except Exception as e:
            self._status_lbl.setText("Pruefung fehlgeschlagen")
            self._status_lbl.setStyleSheet(f"color: {C_ERROR}; font-size: 13px;")
            self._detail_lbl.setText(str(e))

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(C_SURFACE))
        p.drawRoundedRect(self.rect(), 12, 12)
        p.setPen(QPen(QColor(C_BORDER), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(self.rect().adjusted(0,0,-1,-1), 12, 12)
        # Accent top bar
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(C_ACCENT))
        p.drawRoundedRect(0, 0, self.width(), 3, 1, 1)
        p.end()

# ══════════════════════════════════════════════════════════════════════════════
# Log Panel
# ══════════════════════════════════════════════════════════════════════════════
class LogPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(120)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setFixedHeight(24)
        header.setStyleSheet(
            f"background: {C_SURFACE2}; border-top: 1px solid {C_BORDER};"
        )
        hl = QHBoxLayout(header)
        hl.setContentsMargins(12, 0, 10, 0)
        log_title = QLabel("LOG")
        log_title.setStyleSheet(
            f"color: {C_MUTED}; font-size: 10px; letter-spacing: 2px; border:none;"
        )
        hl.addWidget(log_title)
        hl.addStretch()
        clear_btn = QPushButton("Clear")
        clear_btn.setFixedHeight(16)
        clear_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {C_MUTED}; border: none;"
            f"font-size: 10px; padding: 0 6px; }}"
            f"QPushButton:hover {{ color: {C_TEXT}; }}"
        )
        clear_btn.clicked.connect(self._clear)
        hl.addWidget(clear_btn)
        layout.addWidget(header)

        self._text = QTextEdit()
        self._text.setObjectName("log")
        self._text.setReadOnly(True)
        self._text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout.addWidget(self._text)

        _log_signals.message.connect(self._append)

    def _append(self, html: str):
        self._text.append(html)
        self._text.moveCursor(QTextCursor.End)

    def _clear(self):
        self._text.clear()
        log_info("Log cleared")

# ══════════════════════════════════════════════════════════════════════════════
# Save Bar
# ══════════════════════════════════════════════════════════════════════════════
class SaveBar(QWidget):
    def __init__(self, tabs: QTabWidget, parent=None):
        super().__init__(parent)
        self.setObjectName("save_bar")
        self.setFixedHeight(52)
        self._tabs = tabs

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(12)

        self._hint = QLabel("")
        self._hint.setStyleSheet(f"color: {C_MUTED}; font-size: 11px;")
        layout.addWidget(self._hint)
        layout.addStretch()

        self._save_btn = QPushButton("  Save & Send  ▶")
        self._save_btn.setObjectName("accent")
        self._save_btn.setFixedWidth(230)
        self._save_btn.setFixedHeight(36)
        self._save_btn.clicked.connect(self._on_save)
        layout.addWidget(self._save_btn)

        tabs.currentChanged.connect(self._update_hint)
        self._update_hint(0)

    HINTS = {
        0: "Configure lighting effect and send to mouse",
        1: "Configure debounce time and send to mouse",
        2: "Read battery level from mouse",
    }

    def _update_hint(self, idx: int):
        self._hint.setText(self.HINTS.get(idx, ""))

    def _on_save(self):
        idx = self._tabs.currentIndex()
        widget = self._tabs.widget(idx)
        tab_name = self._tabs.tabText(idx).strip()
        log_info(f"Save triggered (tab: {tab_name})")
        if hasattr(widget, "trigger_apply"):
            widget.trigger_apply()

# ══════════════════════════════════════════════════════════════════════════════
# Header
# ══════════════════════════════════════════════════════════════════════════════
class Header(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(56)
        # CSS border-bottom avoids the visual glitch from paintEvent overdraw
        self.setStyleSheet(
            f"QWidget {{ background: {C_SURFACE}; border-bottom: 2px solid {C_ACCENT}; }}"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(22, 0, 22, 0)

        icon = QLabel("◈")
        icon.setStyleSheet(f"color: {C_ACCENT}; font-size: 20px;")
        layout.addWidget(icon)

        title = QLabel("GLORIOUS MODEL O")
        title.setStyleSheet(
            f"color: {C_TEXT}; font-size: 15px; letter-spacing: 3px;"
            f"font-weight: bold; margin-left:4px;"
        )
        layout.addWidget(title)

        sub = QLabel("wireless control panel")
        sub.setStyleSheet(
            f"color: {C_MUTED}; font-size: 11px; letter-spacing: 2px; margin-left: 10px;"
        )
        layout.addWidget(sub)
        layout.addStretch()

        if BACKEND_AVAILABLE:
            dot = QLabel("● CONNECTED")
            dot.setStyleSheet(f"color: {C_SUCCESS}; font-size: 11px; letter-spacing:1px;")
        else:
            dot = QLabel("● NO BACKEND")
            dot.setStyleSheet(f"color: {C_ERROR}; font-size: 11px; letter-spacing:1px;")
        layout.addWidget(dot)

# ══════════════════════════════════════════════════════════════════════════════
# Main Window
# ══════════════════════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Glorious Model O — Control Panel")
        self.setMinimumSize(640, 660)
        self.resize(720, 720)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(Header())

        body = QWidget()
        body.setStyleSheet(f"background: {C_BG};")
        body_l = QVBoxLayout(body)
        body_l.setContentsMargins(14, 14, 14, 0)
        body_l.setSpacing(0)

        self.tabs = QTabWidget()
        self._lighting_tab = LightingTab()
        self._settings_tab = SettingsTab()
        self._battery_tab  = BatteryTab()
        self.tabs.addTab(self._lighting_tab, "  Lighting  ")
        self.tabs.addTab(self._settings_tab, "  Settings  ")
        self.tabs.addTab(self._battery_tab,  "  Battery  ")
        body_l.addWidget(self.tabs)
        root.addWidget(body, stretch=1)

        root.addWidget(SaveBar(self.tabs))
        root.addWidget(LogPanel())

        log_info("Main window opened")

# ══════════════════════════════════════════════════════════════════════════════
# Permission check  (HID access without sudo via udev rule)
# ══════════════════════════════════════════════════════════════════════════════
UDEV_CMD = (
    "echo 'SUBSYSTEM==\"hidraw\", ATTRS{idVendor}==\"258a\","
    " ATTRS{idProduct}==\"2022\", MODE=\"0666\", GROUP=\"plugdev\"'"
    " | sudo tee /etc/udev/rules.d/99-glorious-mouse.rules"
    " && sudo udevadm control --reload-rules"
    " && sudo udevadm trigger"
    " && sudo usermod -aG plugdev $USER"
)

def _hid_accessible() -> bool:
    """Return True if the HID device can be opened without root."""
    try:
        import hid as _hid
        # Just enumerate — doesn't open the device, no root needed for this
        devs = _hid.enumerate(0x258a, 0x2022)
        if not devs:
            return True   # mouse not connected — don't block startup
        # Try actually opening it
        d = _hid.Device(0x258a, 0x2022)
        d.close()
        return True
    except Exception:
        return False

def _show_permissions_dialog(app):
    dlg = QDialog()
    dlg.setWindowTitle("Setup Required")
    dlg.setFixedSize(560, 310)
    dlg.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)

    layout = QVBoxLayout(dlg)
    layout.setContentsMargins(30, 30, 30, 22)
    layout.setSpacing(14)

    # Title row
    title_row = QHBoxLayout()
    icon = QLabel("◈")
    icon.setStyleSheet(f"color: {C_ERROR}; font-size: 22px;")
    title_row.addWidget(icon)
    title = QLabel("One-Time Setup Required")
    title.setStyleSheet(
        f"color: {C_TEXT}; font-size: 15px; font-weight: bold; margin-left: 6px;"
    )
    title_row.addWidget(title)
    title_row.addStretch()
    layout.addLayout(title_row)

    sep = QFrame()
    sep.setFrameShape(QFrame.HLine)
    sep.setStyleSheet(f"color: {C_BORDER};")
    layout.addWidget(sep)

    desc = QLabel(
        "The app needs permission to access the mouse via HID.\n"
        "Run this command once in a terminal, then re-login and restart the app:"
    )
    desc.setStyleSheet(f"color: {C_MUTED}; font-size: 12px;")
    desc.setWordWrap(True)
    layout.addWidget(desc)

    # Copyable command field
    cmd_field = QLineEdit(UDEV_CMD)
    cmd_field.setReadOnly(True)
    cmd_field.setStyleSheet(
        f"background: #0D0E12; color: {C_ACCENT}; border: 1px solid {C_BORDER};"
        f"border-radius: 6px; padding: 8px 12px; font-size: 11px;"
        f"font-family: \'JetBrains Mono\', \'Fira Code\', \'Consolas\', monospace;"
        f"selection-background-color: {C_ACCENT}; selection-color: #000;"
    )
    cmd_field.home(False)
    layout.addWidget(cmd_field)

    note = QLabel("After running the command: log out, log back in, then relaunch the app.")
    note.setStyleSheet(f"color: {C_MUTED}; font-size: 11px;")
    note.setWordWrap(True)
    layout.addWidget(note)

    layout.addStretch()

    btn_row = QHBoxLayout()
    btn_row.addStretch()

    copy_btn = QPushButton("  Copy Command  ⎘")
    copy_btn.setFixedWidth(180)
    copy_btn.clicked.connect(lambda: (
        app.clipboard().setText(UDEV_CMD),
        copy_btn.setText("  Copied!  ✓"),
        QTimer.singleShot(2000, lambda: copy_btn.setText("  Copy Command  ⎘"))
    ))
    btn_row.addWidget(copy_btn)

    exit_btn = QPushButton("Exit")
    exit_btn.setObjectName("accent")
    exit_btn.setFixedWidth(100)
    exit_btn.clicked.connect(dlg.reject)
    btn_row.addWidget(exit_btn)
    layout.addLayout(btn_row)

    def _paint(event):
        p = QPainter(dlg)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(C_SURFACE))
        p.drawRoundedRect(dlg.rect(), 12, 12)
        p.setPen(QPen(QColor(C_BORDER), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(dlg.rect().adjusted(0,0,-1,-1), 12, 12)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(C_ERROR))
        p.drawRoundedRect(0, 0, dlg.width(), 3, 1, 1)
        p.end()
    dlg.paintEvent = _paint
    return dlg.exec()

# ══════════════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════════════
def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    app.setApplicationName("Glorious Control Panel")

    palette = QPalette()
    palette.setColor(QPalette.Window,          QColor(C_BG))
    palette.setColor(QPalette.WindowText,      QColor(C_TEXT))
    palette.setColor(QPalette.Base,            QColor(C_SURFACE2))
    palette.setColor(QPalette.AlternateBase,   QColor(C_SURFACE))
    palette.setColor(QPalette.Text,            QColor(C_TEXT))
    palette.setColor(QPalette.Button,          QColor(C_SURFACE2))
    palette.setColor(QPalette.ButtonText,      QColor(C_TEXT))
    palette.setColor(QPalette.Highlight,       QColor(C_ACCENT))
    palette.setColor(QPalette.HighlightedText, QColor("#000"))
    app.setPalette(palette)

    # ── Permission check ─────────────────────────────────────────────────────
    if os.name == "posix" and not _hid_accessible():
        result = _show_permissions_dialog(app)
        sys.exit(0)

    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()