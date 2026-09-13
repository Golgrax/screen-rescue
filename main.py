#!/usr/bin/env python3
"""
ScreenRescue - Android Recovery, Screen Mirroring, and Automation Utility
Author: Karl Benjamin Bughaw (Golgrax)
"""

import sys
import os
import time
import subprocess
import threading
import signal
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QCheckBox, QTabWidget,
    QTextEdit, QGroupBox, QGridLayout, QFrame, QMessageBox, QProgressBar,
    QFileDialog, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QPointF, QRectF
from PyQt6.QtGui import QIcon, QFont, QColor, QPainter, QPen, QBrush, QLinearGradient, QPainterPath

APP_DIR = Path(__file__).resolve().parent
ICON_PATH = APP_DIR / "icon.png"

# Standalone 326-byte ARM64 ELF binary that exclusively isolates /dev/input/event0
# via EVIOCGRAB (0x40044590) ioctl to shield against water-damaged shorting buttons.
EVGRAB_ARM64_BIN = (
    b'\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\xb7\x00\x01\x00\x00\x00x\x00@\x00\x00\x00\x00\x00'
    b'@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00@\x008\x00\x01\x00\x00\x00\x00\x00\x00\x00'
    b'\x01\x00\x00\x00\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00'
    b'F\x01\x00\x00\x00\x00\x00\x00F\x01\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\xe0\x03@\xf9\x1f\x04\x00\xf1'
    b'l\x00\x00TA\x05\x00\x10\x02\x00\x00\x14\xe1\x0b@\xf9`\x0c\x80\x92\x02\x00\x80\xd2\x03\x00\x80\xd2\x08\x07\x80\xd2\x01\x00'
    b'\x00\xd4\x1f\x00\x00\xf1K\x03\x00T\xf3\x03\x00\xaa\xe0\x03\x13\xaa\x01\xb2\x88\xd2\x81\x00\xa8\xf2"\x00\x80\xd2\xa8\x03'
    b'\x80\xd2\x01\x00\x00\xd4\x1f\x00\x00\xf1\x8b\x02\x00T \x00\x80\xd2A\x03\x00P\x02\x01\x80\xd2\x08\x08\x80\xd2\x01\x00\x00\xd4'
    b'\xff\x03\x01\xd1\xe0\x03\x13\xaa\xe1\x03\x00\x91\x02\x08\x80\xd2\xe8\x07\x80\xd2\x01\x00\x00\xd4\x1f\x00\x00\xf1L\xff\xff'
    b'T\x00\x00\x80\xd2\xa8\x0b\x80\xd2\x01\x00\x00\xd4\xe0\x03\x00\xcb\xa8\x0b\x80\xd2\x01\x00\x00\xd4\xe0\x03\x00\xcb\x00\x90'
    b'\x01\x91\xa8\x0b\x80\xd2\x01\x00\x00\xd4/dev/input/event0\x00GRABBED\n'
)

DARK_STYLE = """
QMainWindow {
    background-color: #0b0f19;
}
QWidget {
    color: #e2e8f0;
    font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    font-size: 13px;
}
QGroupBox {
    border: 1px solid #1e293b;
    border-radius: 10px;
    margin-top: 14px;
    padding-top: 14px;
    background-color: #111827;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    padding: 0 6px;
    color: #38bdf8;
}
QTabWidget::pane {
    border: 1px solid #1e293b;
    border-radius: 8px;
    background-color: #0f172a;
}
QTabBar::tab {
    background: #1e293b;
    color: #94a3b8;
    padding: 10px 18px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 600;
}
QTabBar::tab:selected {
    background: #0284c7;
    color: #ffffff;
}
QTabBar::tab:hover:!selected {
    background: #334155;
    color: #f1f5f9;
}
QPushButton {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
    color: #f8fafc;
}
QPushButton:hover {
    background-color: #2563eb;
    border-color: #3b82f6;
}
QPushButton:pressed {
    background-color: #1d4ed8;
}
QPushButton:disabled {
    background-color: #1e293b;
    color: #475569;
    border-color: #1e293b;
}
QPushButton#actionPrimary {
    background-color: #0284c7;
    border: 1px solid #38bdf8;
    color: #ffffff;
    font-size: 14px;
    padding: 10px 20px;
}
QPushButton#actionPrimary:hover {
    background-color: #0369a1;
}
QPushButton#actionDanger {
    background-color: #991b1b;
    border: 1px solid #ef4444;
}
QPushButton#actionDanger:hover {
    background-color: #b91c1c;
}
QPushButton#actionSuccess {
    background-color: #065f46;
    border: 1px solid #10b981;
}
QPushButton#actionSuccess:hover {
    background-color: #047857;
}
QLineEdit, QComboBox {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px 12px;
    color: #f8fafc;
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #38bdf8;
}
QTextEdit {
    background-color: #030712;
    border: 1px solid #1f2937;
    border-radius: 6px;
    color: #4ade80;
    font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
    font-size: 12px;
}
QCheckBox {
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #475569;
    background-color: #1e293b;
}
QCheckBox::indicator:checked {
    background-color: #0284c7;
    border-color: #38bdf8;
}
"""

def find_scrcpy_window(pid=None, timeout=4.0):
    """Safely poll for a scrcpy window by PID or WM_CLASS without throwing exceptions."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if pid:
            try:
                res = subprocess.run(["xdotool", "search", "--pid", str(pid)], capture_output=True, text=True)
                if res.returncode == 0:
                    wids = res.stdout.strip().split()
                    if wids:
                        return wids[-1]
            except Exception:
                pass
        # Fallback to WM_CLASS search
        try:
            res = subprocess.run(["xdotool", "search", "--class", "scrcpy"], capture_output=True, text=True)
            if res.returncode == 0:
                wids = res.stdout.strip().split()
                if wids:
                    return wids[-1]
        except Exception:
            pass
        time.sleep(0.25)
    return None


class PatternLockWidget(QWidget):
    patternChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 220)
        self.nodes = []
        self.hover_pos = None
        self.is_drawing = False

    def reset_pattern(self):
        self.nodes.clear()
        self.hover_pos = None
        self.update()
        self.patternChanged.emit("")

    def get_node_coords(self, index):
        idx = index - 1
        r = idx // 3
        c = idx % 3
        margin = 35
        spacing = (self.width() - 2 * margin) / 2
        x = margin + c * spacing
        y = margin + r * spacing
        return QPointF(x, y)

    def get_node_at(self, pos):
        for i in range(1, 10):
            p = self.get_node_coords(i)
            dist = ((pos.x() - p.x()) ** 2 + (pos.y() - p.y()) ** 2) ** 0.5
            if dist <= 24:
                return i
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.nodes.clear()
            self.is_drawing = True
            node = self.get_node_at(event.position())
            if node:
                self.nodes.append(node)
                self.patternChanged.emit("-".join(map(str, self.nodes)))
            self.hover_pos = event.position()
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_drawing:
            self.hover_pos = event.position()
            node = self.get_node_at(event.position())
            if node and node not in self.nodes:
                self.nodes.append(node)
                self.patternChanged.emit("-".join(map(str, self.nodes)))
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_drawing = False
            self.hover_pos = None
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.fillRect(self.rect(), QColor("#111827"))

        if len(self.nodes) > 1:
            pen = QPen(QColor("#38bdf8"), 5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            for i in range(len(self.nodes) - 1):
                p1 = self.get_node_coords(self.nodes[i])
                p2 = self.get_node_coords(self.nodes[i+1])
                painter.drawLine(p1, p2)

        if self.is_drawing and self.hover_pos and self.nodes:
            pen = QPen(QColor("#0284c7"), 3, Qt.PenStyle.DashLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            p1 = self.get_node_coords(self.nodes[-1])
            painter.drawLine(p1, self.hover_pos)

        for i in range(1, 10):
            p = self.get_node_coords(i)
            if i in self.nodes:
                painter.setPen(QPen(QColor("#38bdf8"), 3))
                painter.setBrush(QBrush(QColor("#0284c7")))
                painter.drawEllipse(p, 16, 16)
                painter.setBrush(QBrush(QColor("#ffffff")))
                painter.drawEllipse(p, 6, 6)
            else:
                painter.setPen(QPen(QColor("#475569"), 2))
                painter.setBrush(QBrush(QColor("#1e293b")))
                painter.drawEllipse(p, 12, 12)


class Bridge(QObject):
    """Thread-safe signal bridge for Qt GUI updates."""
    log_msg = pyqtSignal(str)
    update_status = pyqtSignal(str, str, str)  # serial, state, model
    set_unlock_enabled = pyqtSignal(bool)
    set_auth_enabled = pyqtSignal(bool)
    set_backup_ui = pyqtSignal(bool)
    set_clear_lock_enabled = pyqtSignal(bool)


class ScreenRescueApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ScreenRescue - Android Recovery and Mirroring Utility")
        self.setMinimumSize(860, 680)
        self.resize(920, 740)
        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))

        self.setStyleSheet(DARK_STYLE)

        self.scrcpy_proc = None
        self.current_serial = None
        self.device_state = "disconnected"

        # Thread-safe signal bridge
        self.bridge = Bridge()
        self.bridge.log_msg.connect(self._log_on_main_thread)
        self.bridge.update_status.connect(self._update_status_on_main_thread)

        self.init_ui()

        # Connect button control signals after UI init
        self.bridge.set_unlock_enabled.connect(self.btn_unlock.setEnabled)
        self.bridge.set_clear_lock_enabled.connect(self.btn_clear_lock.setEnabled)
        self.bridge.set_auth_enabled.connect(self.btn_auto_authorize.setEnabled)
        self.bridge.set_backup_ui.connect(self._set_backup_ui_state)

        # Polling timer
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.trigger_status_check)
        self.poll_timer.start(2500)
        QTimer.singleShot(500, self.trigger_status_check)

        # Start anti-sleep watchdog thread
        self.start_watchdog_thread()

    def _log_on_main_thread(self, text):
        timestamp = time.strftime("%H:%M:%S")
        self.log_view.append(f"[{timestamp}] {text}")

    def log(self, text):
        """Thread-safe log dispatcher."""
        self.bridge.log_msg.emit(text)

    def _update_status_on_main_thread(self, serial, state, model):
        self.current_serial = serial
        self.device_state = state

        if state == "device":
            self.status_badge.setText(f"Connected: {model} ({serial})")
            self.status_badge.setStyleSheet(
                "background-color: #064e3b; color: #6ee7b7; border: 1px solid #10b981; "
                "border-radius: 20px; padding: 6px 16px; font-weight: bold;"
            )
            self.btn_start_mirror.setEnabled(True)
        elif state == "unauthorized":
            self.status_badge.setText(f"Unauthorized: {serial} (Action Required in Tab 3)")
            self.status_badge.setStyleSheet(
                "background-color: #78350f; color: #fde68a; border: 1px solid #f59e0b; "
                "border-radius: 20px; padding: 6px 16px; font-weight: bold;"
            )
            self.btn_start_mirror.setEnabled(False)
        else:
            self.status_badge.setText("No Device Detected (Connect via USB)")
            self.status_badge.setStyleSheet(
                "background-color: #7f1d1d; color: #fca5a5; border: 1px solid #ef4444; "
                "border-radius: 20px; padding: 6px 16px; font-weight: bold;"
            )
            self.btn_start_mirror.setEnabled(False)

    def _set_backup_ui_state(self, running):
        self.btn_quick_backup.setEnabled(not running)
        if running:
            self.backup_progress.show()
        else:
            self.backup_progress.hide()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setSpacing(12)
        root_layout.setContentsMargins(16, 16, 16, 16)

        # Top Bar
        top_bar = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("ScreenRescue")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #38bdf8;")
        subtitle = QLabel("Android Device Recovery, Mirroring, and Automation Utility")
        subtitle.setStyleSheet("color: #94a3b8; font-size: 12px;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        top_bar.addLayout(title_box)

        top_bar.addStretch()

        self.status_badge = QLabel("Checking devices...")
        self.status_badge.setStyleSheet(
            "background-color: #1e293b; color: #cbd5e1; border: 1px solid #334155; "
            "border-radius: 20px; padding: 6px 16px; font-weight: bold;"
        )
        top_bar.addWidget(self.status_badge)

        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self.trigger_status_check)
        top_bar.addWidget(self.btn_refresh)

        root_layout.addLayout(top_bar)

        # Tabs
        tabs = QTabWidget()

        tab_mirror = QWidget()
        self.setup_mirror_tab(tab_mirror)
        tabs.addTab(tab_mirror, "Screen Mirroring")

        tab_unlock = QWidget()
        self.setup_unlock_tab(tab_unlock)
        tabs.addTab(tab_unlock, "Blind Unlocker")

        tab_authorize = QWidget()
        self.setup_authorize_tab(tab_authorize)
        tabs.addTab(tab_authorize, "Authorize ADB")

        tab_backup = QWidget()
        self.setup_backup_tab(tab_backup)
        tabs.addTab(tab_backup, "File Recovery")

        root_layout.addWidget(tabs, 3)

        # Bottom Log Box
        log_group = QGroupBox("Operation Logs and Diagnostics")
        log_layout = QVBoxLayout(log_group)
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setPlaceholderText("Ready. Connect device via USB...")
        log_layout.addWidget(self.log_view)

        log_actions = QHBoxLayout()
        btn_clear_log = QPushButton("Clear Log")
        btn_clear_log.clicked.connect(self.log_view.clear)
        log_actions.addStretch()
        log_actions.addWidget(btn_clear_log)
        log_layout.addLayout(log_actions)

        root_layout.addWidget(log_group, 2)

    def setup_mirror_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(14)
        layout.setContentsMargins(16, 16, 16, 16)

        desc = QLabel(
            "<b>Screen Mirroring and Digitizer Suppression</b><br>"
            "Streams Android display to the host PC while powering off the physical screen (-S) to "
            "suppress erratic touch digitizer input."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        opt_group = QGroupBox("Mirroring Options")
        opt_layout = QGridLayout(opt_group)

        self.cb_turn_screen_off = QCheckBox("Turn Physical Screen Off (-S) [Suppresses ghost touches]")
        self.cb_turn_screen_off.setChecked(True)
        self.cb_turn_screen_off.setStyleSheet("color: #38bdf8; font-weight: bold;")
        opt_layout.addWidget(self.cb_turn_screen_off, 0, 0, 1, 2)

        self.cb_stay_awake = QCheckBox("Keep Device Awake (-w)")
        self.cb_stay_awake.setChecked(True)
        opt_layout.addWidget(self.cb_stay_awake, 1, 0)

        self.cb_forward_audio = QCheckBox("Forward Audio (Android 11+)")
        self.cb_forward_audio.setChecked(True)
        opt_layout.addWidget(self.cb_forward_audio, 1, 1)

        opt_layout.addWidget(QLabel("Max Video Resolution:"), 2, 0)
        self.combo_resolution = QComboBox()
        self.combo_resolution.addItems(["Native", "1080p", "720p", "480p"])
        self.combo_resolution.setCurrentIndex(0)
        opt_layout.addWidget(self.combo_resolution, 2, 1)

        layout.addWidget(opt_group)

        watchdog_group = QGroupBox("Hardware Buttons, Power, and Mistouch Shield")
        watchdog_layout = QVBoxLayout(watchdog_group)

        self.cb_hardware_button_shield = QCheckBox("Mute Physical Side Buttons (Volume/Power Hardware Short Shield)")
        self.cb_hardware_button_shield.setChecked(True)
        self.cb_hardware_button_shield.setStyleSheet("color: #38bdf8; font-weight: bold;")
        self.cb_hardware_button_shield.toggled.connect(self.on_toggle_button_shield)
        watchdog_layout.addWidget(self.cb_hardware_button_shield)

        self.cb_anti_sleep_watchdog = QCheckBox("Keep-Awake Watchdog (Revives display if sleep occurs)")
        self.cb_anti_sleep_watchdog.setChecked(True)
        self.cb_anti_sleep_watchdog.setStyleSheet("color: #38bdf8; font-weight: bold;")
        watchdog_layout.addWidget(self.cb_anti_sleep_watchdog)

        ctrl_box = QHBoxLayout()
        ctrl_box.addWidget(QLabel("Software Controls:"))
        self.btn_vol_down = QPushButton("Vol -")
        self.btn_vol_down.setToolTip("Trigger Volume Down keyevent (25)")
        self.btn_vol_down.clicked.connect(lambda: self.send_software_key(25, "Volume Down"))
        ctrl_box.addWidget(self.btn_vol_down)

        self.btn_vol_up = QPushButton("Vol +")
        self.btn_vol_up.setToolTip("Trigger Volume Up keyevent (24)")
        self.btn_vol_up.clicked.connect(lambda: self.send_software_key(24, "Volume Up"))
        ctrl_box.addWidget(self.btn_vol_up)

        self.btn_power_key = QPushButton("Power")
        self.btn_power_key.setToolTip("Trigger Power keyevent (26)")
        self.btn_power_key.clicked.connect(lambda: self.send_software_key(26, "Power"))
        ctrl_box.addWidget(self.btn_power_key)

        self.btn_wake_key = QPushButton("Wake")
        self.btn_wake_key.setToolTip("Trigger Wakeup keyevent (224)")
        self.btn_wake_key.clicked.connect(lambda: self.send_software_key(224, "Wakeup"))
        ctrl_box.addWidget(self.btn_wake_key)
        watchdog_layout.addLayout(ctrl_box)

        self.btn_apply_anti_sleep = QPushButton("Apply Anti-Sleep & Shield Settings")
        self.btn_apply_anti_sleep.clicked.connect(self.apply_anti_sleep_settings)
        watchdog_layout.addWidget(self.btn_apply_anti_sleep)
        layout.addWidget(watchdog_group)

        btn_layout = QHBoxLayout()
        self.btn_start_mirror = QPushButton("Launch Screen Mirror")
        self.btn_start_mirror.setObjectName("actionPrimary")
        self.btn_start_mirror.setFixedHeight(48)
        self.btn_start_mirror.clicked.connect(self.launch_scrcpy)
        btn_layout.addWidget(self.btn_start_mirror, 2)

        self.btn_toggle_screen = QPushButton("Toggle Physical Screen (Alt+O)")
        self.btn_toggle_screen.setFixedHeight(48)
        self.btn_toggle_screen.setToolTip("Toggle physical display panel state via scrcpy Alt+O")
        self.btn_toggle_screen.clicked.connect(self.toggle_physical_screen)
        btn_layout.addWidget(self.btn_toggle_screen, 1)

        self.btn_stop_mirror = QPushButton("Stop Mirror")
        self.btn_stop_mirror.setObjectName("actionDanger")
        self.btn_stop_mirror.setFixedHeight(48)
        self.btn_stop_mirror.clicked.connect(self.stop_scrcpy)
        btn_layout.addWidget(self.btn_stop_mirror, 1)

        layout.addLayout(btn_layout)
        layout.addStretch()

    def setup_unlock_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(14)
        layout.setContentsMargins(16, 16, 16, 16)

        info = QLabel(
            "<b>Blind Credential Unlock</b><br>"
            "Submits unlock credentials directly via ADB hardware keyevents or USB HID keyboard emulation."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        mode_box = QHBoxLayout()
        mode_box.addWidget(QLabel("<b>Lock Type:</b>"))
        self.combo_lock_type = QComboBox()
        self.combo_lock_type.addItems(["PIN (Numeric)", "Password (Alphanumeric)", "Pattern (3x3 Grid)", "Swipe Only (No Lock)"])
        self.combo_lock_type.currentIndexChanged.connect(self.on_lock_type_changed)
        mode_box.addWidget(self.combo_lock_type)
        mode_box.addStretch()
        layout.addLayout(mode_box)

        self.input_card = QGroupBox("Enter Unlock Credentials")
        input_layout = QVBoxLayout(self.input_card)

        self.pin_row = QHBoxLayout()
        self.pin_label = QLabel("PIN Code:")
        self.pin_entry = QLineEdit()
        self.pin_entry.setPlaceholderText("e.g. 1113")
        self.pin_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.btn_show_pin = QPushButton("Show")
        self.btn_show_pin.setFixedWidth(54)
        self.btn_show_pin.clicked.connect(self.toggle_pin_visibility)
        self.pin_row.addWidget(self.pin_label)
        self.pin_row.addWidget(self.pin_entry)
        self.pin_row.addWidget(self.btn_show_pin)
        input_layout.addLayout(self.pin_row)

        self.pattern_container = QWidget()
        pat_layout = QHBoxLayout(self.pattern_container)
        self.pattern_widget = PatternLockWidget()
        self.pattern_display = QLabel("No pattern drawn")
        self.pattern_display.setStyleSheet("font-size: 14px; font-weight: bold; color: #38bdf8;")
        self.pattern_widget.patternChanged.connect(self.on_pattern_drawn)

        pat_info_box = QVBoxLayout()
        pat_info_box.addWidget(QLabel("<b>Draw pattern on grid:</b>"))
        pat_info_box.addWidget(self.pattern_display)
        btn_reset_pattern = QPushButton("Clear Pattern")
        btn_reset_pattern.clicked.connect(self.pattern_widget.reset_pattern)
        pat_info_box.addWidget(btn_reset_pattern)
        pat_info_box.addStretch()

        pat_layout.addWidget(self.pattern_widget)
        pat_layout.addLayout(pat_info_box)
        input_layout.addWidget(self.pattern_container)
        self.pattern_container.hide()

        layout.addWidget(self.input_card)

        method_group = QGroupBox("Unlock Method")
        method_layout = QVBoxLayout(method_group)
        self.cb_use_otg = QCheckBox("Force USB OTG Keyboard Mode (Use only if ADB is unauthorized)")
        self.cb_use_otg.setChecked(False)
        method_layout.addWidget(self.cb_use_otg)
        layout.addWidget(method_group)

        self.btn_unlock = QPushButton("Unlock Device")
        self.btn_unlock.setObjectName("actionPrimary")
        self.btn_unlock.setFixedHeight(48)
        self.btn_unlock.clicked.connect(self.run_blind_unlock)
        layout.addWidget(self.btn_unlock)

        self.btn_clear_lock = QPushButton("Clear Lockscreen Credential (locksettings)")
        self.btn_clear_lock.setObjectName("actionDanger")
        self.btn_clear_lock.setFixedHeight(42)
        self.btn_clear_lock.clicked.connect(self.run_clear_lockscreen)
        layout.addWidget(self.btn_clear_lock)

        layout.addStretch()

    def on_lock_type_changed(self, index):
        if index == 0:
            self.pin_label.show()
            self.pin_entry.show()
            self.btn_show_pin.show()
            self.pin_label.setText("PIN Code:")
            self.pin_entry.setPlaceholderText("e.g. 1113")
            self.pattern_container.hide()
        elif index == 1:
            self.pin_label.show()
            self.pin_entry.show()
            self.btn_show_pin.show()
            self.pin_label.setText("Password:")
            self.pin_entry.setPlaceholderText("Enter alphanumeric password")
            self.pattern_container.hide()
        elif index == 2:
            self.pin_label.hide()
            self.pin_entry.hide()
            self.btn_show_pin.hide()
            self.pattern_container.show()
        elif index == 3:
            self.pin_label.hide()
            self.pin_entry.hide()
            self.btn_show_pin.hide()
            self.pattern_container.hide()

    def toggle_pin_visibility(self):
        if self.pin_entry.echoMode() == QLineEdit.EchoMode.Password:
            self.pin_entry.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_show_pin.setText("Hide")
        else:
            self.pin_entry.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_show_pin.setText("Show")

    def on_pattern_drawn(self, pat_str):
        if pat_str:
            self.pattern_display.setText(f"Sequence: {pat_str}")
        else:
            self.pattern_display.setText("No pattern drawn")

    def setup_authorize_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(14)
        layout.setContentsMargins(16, 16, 16, 16)

        info = QLabel(
            "<b>ADB Authorization Automation</b><br><br>"
            "When connecting via USB with debugging enabled, Android presents an authorization dialog. "
            "If the screen is damaged, this routine establishes a pure USB OTG keyboard connection "
            "and dispatches navigation keystrokes (<code>Tab -> Tab -> Right -> Enter</code>) to approve the prompt."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        box = QGroupBox("Authorization Automation")
        box_layout = QVBoxLayout(box)

        step1 = QLabel("1. Connect device via USB and ensure device is unlocked.")
        step2 = QLabel("2. Click the button below. Leave mouse and keyboard undisturbed during execution.")
        step3 = QLabel("3. Keystroke sequence will be dispatched via OTG.")
        box_layout.addWidget(step1)
        box_layout.addWidget(step2)
        box_layout.addWidget(step3)

        layout.addWidget(box)

        self.btn_auto_authorize = QPushButton("Authorize ADB via USB OTG")
        self.btn_auto_authorize.setObjectName("actionSuccess")
        self.btn_auto_authorize.setFixedHeight(48)
        self.btn_auto_authorize.clicked.connect(self.run_auto_authorize)
        layout.addWidget(self.btn_auto_authorize)

        layout.addStretch()

    def setup_backup_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(14)
        layout.setContentsMargins(16, 16, 16, 16)

        desc = QLabel(
            "<b>Local Data Recovery</b><br>"
            "Access internal shared storage via GVFS MTP or extract standard storage directories to the host."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        btn_box = QHBoxLayout()
        self.btn_open_mtp = QPushButton("Open MTP Storage in File Manager")
        self.btn_open_mtp.setFixedHeight(44)
        self.btn_open_mtp.clicked.connect(self.open_mtp_storage)
        btn_box.addWidget(self.btn_open_mtp)

        self.btn_quick_backup = QPushButton("Extract Standard Directories (ADB Pull)")
        self.btn_quick_backup.setObjectName("actionPrimary")
        self.btn_quick_backup.setFixedHeight(44)
        self.btn_quick_backup.clicked.connect(self.start_quick_backup)
        btn_box.addWidget(self.btn_quick_backup)

        layout.addLayout(btn_box)

        self.backup_progress = QProgressBar()
        self.backup_progress.setRange(0, 0)
        self.backup_progress.hide()
        layout.addWidget(self.backup_progress)

        layout.addStretch()

    def trigger_status_check(self):
        """Asynchronously query device status and send via thread-safe Qt bridge."""
        def worker():
            dev_found = None
            state = "disconnected"
            model = "Unknown Device"
            try:
                res = subprocess.run(["adb", "devices", "-l"], capture_output=True, text=True, timeout=3)
                lines = res.stdout.strip().splitlines()
                for line in lines[1:]:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        dev_found = parts[0]
                        state = parts[1]
                        for part in parts[2:]:
                            if part.startswith("model:"):
                                model = part.split(":", 1)[1]
                        break
            except Exception:
                pass
            self.bridge.update_status.emit(dev_found or "", state, model)

        threading.Thread(target=worker, daemon=True).start()

    def launch_scrcpy(self):
        if self.scrcpy_proc and self.scrcpy_proc.poll() is None:
            self.log("[WARN] scrcpy is already running.")
            return

        cmd = ["scrcpy"]
        if self.current_serial:
            cmd.extend(["-s", self.current_serial])

        if self.cb_turn_screen_off.isChecked():
            cmd.append("-S")

        if self.cb_stay_awake.isChecked():
            cmd.append("-w")

        if not self.cb_forward_audio.isChecked():
            cmd.append("--no-audio")

        res_choice = self.combo_resolution.currentText()
        if "1080p" in res_choice:
            cmd.extend(["-m", "1080"])
        elif "720p" in res_choice:
            cmd.extend(["-m", "720"])
        elif "480p" in res_choice:
            cmd.extend(["-m", "480"])

        # Apply anti-sleep / anti-lock settings
        self.apply_anti_sleep_settings()

        self.log(f"[INFO] Launching scrcpy: {' '.join(cmd)}")

        try:
            self.scrcpy_proc = subprocess.Popen(cmd)
            self.log("[INFO] Mirroring started. Physical screen is powered off to suppress touch events.")
        except Exception as e:
            self.log(f"[ERROR] Failed to launch scrcpy: {e}")
            QMessageBox.critical(self, "Error", f"Could not launch scrcpy:\n{e}")

    def stop_scrcpy(self):
        if self.scrcpy_proc and self.scrcpy_proc.poll() is None:
            self.scrcpy_proc.terminate()
            self.log("[INFO] Stopped scrcpy mirroring.")
            self.scrcpy_proc = None
        else:
            subprocess.run(["pkill", "-f", "scrcpy"])
            self.log("[INFO] Terminated scrcpy processes.")

    def toggle_physical_screen(self):
        self.log("[INFO] Toggling physical display state via Alt+O...")
        pid = self.scrcpy_proc.pid if self.scrcpy_proc else None

        def worker():
            try:
                win_id = find_scrcpy_window(pid, timeout=2.0)
                if win_id:
                    subprocess.run(["xdotool", "windowactivate", "--sync", win_id], check=True)
                    time.sleep(0.2)
                    subprocess.run(["xdotool", "key", "--window", win_id, "Alt_L+o"], check=True)
                    self.log(f"[INFO] Sent Alt+O to window {win_id}.")
                else:
                    self.log("[WARN] No active scrcpy window found.")
            except Exception as e:
                self.log(f"[WARN] Note: {e}")

        threading.Thread(target=worker, daemon=True).start()

    def run_blind_unlock(self):
        lock_type = self.combo_lock_type.currentIndex()
        pin_code = self.pin_entry.text().strip()
        pattern_nodes = list(self.pattern_widget.nodes)
        force_otg = self.cb_use_otg.isChecked()
        serial = self.current_serial
        state = self.device_state

        if lock_type == 0 and not pin_code:
            QMessageBox.warning(self, "Missing PIN", "Enter numeric PIN code first.")
            return
        if lock_type == 1 and not pin_code:
            QMessageBox.warning(self, "Missing Password", "Enter password first.")
            return
        if lock_type == 2 and not pattern_nodes:
            QMessageBox.warning(self, "Missing Pattern", "Draw pattern on the 3x3 grid first.")
            return

        self.btn_unlock.setEnabled(False)
        self.log("[INFO] Starting blind unlock sequence...")

        def worker():
            try:
                if not force_otg and state == "device":
                    self.log("[INFO] Unlocking via ADB...")
                    # Wake up display
                    subprocess.run(["adb", "shell", "input", "keyevent", "224"])
                    time.sleep(0.3)
                    subprocess.run(["adb", "shell", "input", "keyevent", "82"])
                    time.sleep(0.3)
                    # Swipe up to reveal lock bouncer
                    subprocess.run(["adb", "shell", "input", "swipe", "360", "1200", "360", "200", "200"])
                    time.sleep(0.5)

                    if lock_type == 0:  # PIN
                        self.log("[INFO] Dispatching PIN keyevents...")
                        for char in pin_code:
                            if char.isdigit():
                                keycode = 7 + int(char)  # KEYCODE_0 is 7, KEYCODE_1 is 8...
                                subprocess.run(["adb", "shell", "input", "keyevent", str(keycode)])
                                time.sleep(0.15)
                        time.sleep(0.25)
                        subprocess.run(["adb", "shell", "input", "keyevent", "66"])
                    elif lock_type == 1:  # Password
                        self.log("[INFO] Submitting password text...")
                        subprocess.run(["adb", "shell", "input", "text", pin_code])
                        time.sleep(0.3)
                        subprocess.run(["adb", "shell", "input", "keyevent", "66"])
                    elif lock_type == 2:  # Pattern
                        self.execute_adb_pattern(pattern_nodes)
                    elif lock_type == 3:  # Swipe Only (No Lock)
                        self.log("[INFO] Dismissing keyguard...")
                        subprocess.run(["adb", "shell", "wm", "dismiss-keyguard"])

                    self.log("[SUCCESS] ADB unlock sequence executed.")
                else:
                    self.log("[INFO] Initializing USB OTG keyboard blind unlock...")
                    serial_arg = ["-s", serial] if serial else []
                    cmd = ["scrcpy", "--otg", "--mouse=disabled"] + serial_arg
                    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

                    try:
                        win_id = find_scrcpy_window(proc.pid, timeout=5.0)
                        if not win_id:
                            self.log("[ERROR] Could not detect scrcpy OTG window.")
                            return

                        self.log(f"[INFO] OTG window detected: {win_id}.")
                        subprocess.run(["xdotool", "windowactivate", "--sync", win_id])
                        time.sleep(0.3)

                        # Wake
                        self.log("[INFO] Sending wake keystroke...")
                        subprocess.run(["xdotool", "key", "--window", win_id, "space"])
                        time.sleep(0.5)
                        subprocess.run(["xdotool", "key", "--window", win_id, "Return"])
                        time.sleep(0.5)

                        # Reveal PIN pad
                        self.log("[INFO] Swiping up bouncer...")
                        subprocess.run(["xdotool", "key", "--window", win_id, "Up"])
                        time.sleep(0.3)
                        subprocess.run(["xdotool", "key", "--window", win_id, "space"])
                        time.sleep(0.5)

                        # Clear previous inputs
                        self.log("[INFO] Clearing existing input buffer...")
                        for _ in range(8):
                            subprocess.run(["xdotool", "key", "--window", win_id, "BackSpace"])
                            time.sleep(0.05)

                        if lock_type in (0, 1):
                            self.log("[INFO] Typing credentials via OTG...")
                            for char in pin_code:
                                subprocess.run(["xdotool", "key", "--window", win_id, char])
                                time.sleep(0.15)
                            time.sleep(0.3)
                            subprocess.run(["xdotool", "key", "--window", win_id, "Return"])
                            self.log("[INFO] Submitted credentials.")
                        elif lock_type == 2:
                            self.log("[WARN] Note: Patterns in OTG mode require mouse input. Use ADB mode for pattern unlock.")

                        time.sleep(1.0)
                    finally:
                        proc.send_signal(signal.SIGINT)
                        try:
                            proc.communicate(timeout=2)
                        except Exception:
                            proc.kill()

                    self.log("[SUCCESS] OTG blind unlock completed.")
            except Exception as e:
                self.log(f"[ERROR] Error during unlock: {e}")
            finally:
                self.bridge.set_unlock_enabled.emit(True)
                self.trigger_status_check()

        threading.Thread(target=worker, daemon=True).start()

    def execute_adb_pattern(self, nodes):
        self.log(f"Drawing pattern: {' -> '.join(map(str, nodes))}")
        try:
            res = subprocess.check_output(["adb", "shell", "wm", "size"], text=True)
            w, h = 720, 1600
            for line in res.splitlines():
                if "Physical size:" in line:
                    parts = line.split(":", 1)[1].strip().split("x")
                    w, h = int(parts[0]), int(parts[1])
                    break
        except Exception:
            w, h = 720, 1600

        y_start = 0.55 * h
        y_end = 0.82 * h
        x_start = 0.18 * w
        x_end = 0.82 * w

        def get_point(n):
            idx = n - 1
            row = idx // 3
            col = idx % 3
            px = int(x_start + col * ((x_end - x_start) / 2))
            py = int(y_start + row * ((y_end - y_start) / 2))
            return px, py

        for i in range(len(nodes) - 1):
            x1, y1 = get_point(nodes[i])
            x2, y2 = get_point(nodes[i+1])
            subprocess.run(["adb", "shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), "120"])
            time.sleep(0.05)

    def _deploy_evgrab_daemon(self):
        serial = self.current_serial
        s_arg = ["-s", serial] if serial else []
        try:
            chk = subprocess.run(["adb"] + s_arg + ["shell", "pidof", "evgrab"],
                                 capture_output=True, text=True, timeout=2)
            if chk.stdout.strip():
                return

            test_f = subprocess.run(["adb"] + s_arg + ["shell", "test -f /data/local/tmp/evgrab && echo ok"],
                                    capture_output=True, text=True, timeout=2)
            if "ok" not in test_f.stdout:
                tmp_bin = "/tmp/evgrab_arm64_embedded"
                with open(tmp_bin, "wb") as f:
                    f.write(EVGRAB_ARM64_BIN)
                subprocess.run(["adb"] + s_arg + ["push", tmp_bin, "/data/local/tmp/evgrab"],
                               capture_output=True, timeout=3)
                subprocess.run(["adb"] + s_arg + ["shell", "chmod", "+x", "/data/local/tmp/evgrab"],
                               capture_output=True, timeout=2)

            subprocess.run(
                ["adb"] + s_arg + ["shell", "nohup /data/local/tmp/evgrab /dev/input/event0 >/data/local/tmp/evgrab.log 2>&1 &"],
                capture_output=True, timeout=2
            )
            self.log("[SUCCESS] Hardware button shield active. Physical side buttons (/dev/input/event0) are muted.")
        except Exception as e:
            self.log(f"[WARN] Failed to deploy hardware button shield: {e}")

    def _stop_evgrab_daemon(self):
        serial = self.current_serial
        s_arg = ["-s", serial] if serial else []
        try:
            subprocess.run(["adb"] + s_arg + ["shell", "pkill", "-f", "evgrab"],
                           capture_output=True, timeout=2)
            self.log("[INFO] Hardware button shield disabled. Physical side buttons restored.")
        except Exception as e:
            self.log(f"[WARN] Failed to stop hardware button shield: {e}")

    def on_toggle_button_shield(self, checked: bool):
        if checked:
            threading.Thread(target=self._deploy_evgrab_daemon, daemon=True).start()
        else:
            threading.Thread(target=self._stop_evgrab_daemon, daemon=True).start()

    def send_software_key(self, keycode: int, name: str):
        serial = self.current_serial
        s_arg = ["-s", serial] if serial else []
        def worker():
            try:
                subprocess.run(["adb"] + s_arg + ["shell", "input", "keyevent", str(keycode)],
                               capture_output=True, timeout=2)
                self.log(f"[INFO] Dispatched software keyevent: {name} ({keycode}).")
            except Exception as e:
                self.log(f"[ERROR] Failed to send {name} keyevent: {e}")
        threading.Thread(target=worker, daemon=True).start()

    def apply_anti_sleep_settings(self):
        """Hardens the device against sleeping, screen timeouts, and power button shorts."""
        serial = self.current_serial
        s_arg = ["-s", serial] if serial else []
        self.log("[INFO] Applying anti-sleep and anti-lock settings...")

        cmds = [
            ["adb"] + s_arg + ["shell", "svc", "power", "stayon", "true"],
            ["adb"] + s_arg + ["shell", "settings", "put", "global", "stay_on_while_plugged_in", "7"],
            ["adb"] + s_arg + ["shell", "settings", "put", "secure", "power_button_instantly_locks", "0"],
            ["adb"] + s_arg + ["shell", "settings", "put", "secure", "lock_after_timeout", "2147483647"],
            ["adb"] + s_arg + ["shell", "settings", "put", "system", "screen_off_timeout", "2147483647"],
            ["adb"] + s_arg + ["shell", "settings", "put", "system", "end_button_behavior", "0x1"],
            ["adb"] + s_arg + ["shell", "settings", "put", "secure", "double_tap_to_wake", "0"],
        ]
        for c in cmds:
            try:
                subprocess.run(c, capture_output=True, timeout=2)
            except Exception:
                pass

        if hasattr(self, 'cb_hardware_button_shield') and self.cb_hardware_button_shield.isChecked():
            self._deploy_evgrab_daemon()

        self.log("[SUCCESS] Anti-sleep configuration applied.")

    def run_clear_lockscreen(self):
        """Permanently removes the PIN/password/pattern credential via locksettings."""
        pin_code = self.pin_entry.text().strip()
        if not pin_code:
            QMessageBox.warning(self, "PIN Required", "Enter numeric PIN in the input box above.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Credential Removal",
            "This operation will remove the lock screen credential from the connected device via locksettings.\n\n"
            "Proceed?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        serial = self.current_serial
        s_arg = ["-s", serial] if serial else []
        self.btn_clear_lock.setEnabled(False)
        self.log("[INFO] Clearing lock credential via locksettings...")

        def worker():
            try:
                res = subprocess.run(
                    ["adb"] + s_arg + ["shell", "locksettings", "clear", "--old", pin_code],
                    capture_output=True, text=True, timeout=5
                )
                if "cleared" in res.stdout.lower():
                    self.log("[SUCCESS] Lock credential cleared. Lockscreen disabled.")
                    subprocess.run(["adb"] + s_arg + ["shell", "locksettings", "set-disabled", "true"], capture_output=True)
                    self.log("[INFO] Set lockscreen.disabled = true.")
                else:
                    self.log(f"[WARN] Locksettings output: {res.stdout.strip()} {res.stderr.strip()}")
            except Exception as e:
                self.log(f"[ERROR] Error clearing credential: {e}")
            finally:
                self.bridge.set_clear_lock_enabled.emit(True)
                self.trigger_status_check()

        threading.Thread(target=worker, daemon=True).start()

    def start_watchdog_thread(self):
        """Background daemon that monitors device sleep state and ensures hardware shields stay active."""
        def watchdog_loop():
            while True:
                time.sleep(2)
                try:
                    if self.device_state == "device":
                        if hasattr(self, 'cb_anti_sleep_watchdog') and self.cb_anti_sleep_watchdog.isChecked():
                            res = subprocess.run(
                                ["adb", "shell", "dumpsys", "power"],
                                capture_output=True, text=True, timeout=2
                            )
                            if "mWakefulness=Asleep" in res.stdout:
                                subprocess.run(["adb", "shell", "input", "keyevent", "224"], capture_output=True, timeout=1)
                                self.log("[INFO] Watchdog: device sleep detected. Sent WAKEUP event.")

                        if hasattr(self, 'cb_hardware_button_shield') and self.cb_hardware_button_shield.isChecked():
                            res = subprocess.run(
                                ["adb", "shell", "pidof", "evgrab"],
                                capture_output=True, text=True, timeout=2
                            )
                            if not res.stdout.strip():
                                self._deploy_evgrab_daemon()
                except Exception:
                    pass

        threading.Thread(target=watchdog_loop, daemon=True).start()

    def run_auto_authorize(self):
        self.btn_auto_authorize.setEnabled(False)
        self.log("[INFO] Starting ADB auto-authorization sequence...")
        serial = self.current_serial

        def worker():
            try:
                self.log("[INFO] 1. Reconnecting ADB...")
                subprocess.run(["adb", "reconnect"])
                time.sleep(1.5)

                self.log("[INFO] 2. Launching USB OTG keyboard...")
                serial_arg = ["-s", serial] if serial else []
                proc = subprocess.Popen(["scrcpy", "--otg", "--mouse=disabled"] + serial_arg,
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

                try:
                    win_id = find_scrcpy_window(proc.pid, timeout=5.0)
                    if not win_id:
                        self.log("[ERROR] Could not detect scrcpy OTG window.")
                        return

                    subprocess.run(["xdotool", "windowactivate", "--sync", win_id])
                    time.sleep(0.3)

                    self.log("[INFO] 3. Sending authorization keystrokes (Tab -> Tab -> Right -> Enter)...")
                    subprocess.run(["xdotool", "key", "--window", win_id, "Tab"])
                    time.sleep(0.3)
                    subprocess.run(["xdotool", "key", "--window", win_id, "Tab"])
                    time.sleep(0.3)
                    subprocess.run(["xdotool", "key", "--window", win_id, "Right"])
                    time.sleep(0.3)
                    subprocess.run(["xdotool", "key", "--window", win_id, "Return"])
                    time.sleep(1.0)
                finally:
                    proc.send_signal(signal.SIGINT)
                    try:
                        proc.communicate(timeout=2)
                    except Exception:
                        proc.kill()

                time.sleep(1.0)
                res = subprocess.check_output(["adb", "devices"], text=True)
                if "\tdevice" in res:
                    self.log("[SUCCESS] Host PC authorized successfully.")
                else:
                    self.log("[WARN] Device still unauthorized. Verify device is awake and unlocked.")
            except Exception as e:
                self.log(f"[ERROR] Error during authorization: {e}")
            finally:
                self.bridge.set_auth_enabled.emit(True)
                self.trigger_status_check()

        threading.Thread(target=worker, daemon=True).start()

    def open_mtp_storage(self):
        self.log("[INFO] Opening MTP storage...")
        def worker():
            try:
                gvfs_dir = Path(f"/run/user/{os.getuid()}/gvfs")
                mtp_path = None
                if gvfs_dir.exists():
                    for entry in gvfs_dir.iterdir():
                        if entry.name.startswith("mtp:"):
                            storage = entry / "Internal shared storage"
                            mtp_path = storage if storage.exists() else entry
                            break

                if mtp_path and mtp_path.exists():
                    subprocess.run(["xdg-open", str(mtp_path)])
                    self.log(f"[SUCCESS] Opened storage path: {mtp_path}")
                else:
                    self.log("[INFO] Triggering gio mount for MTP...")
                    subprocess.run(["gio", "mount", "-l"])
                    subprocess.run(["xdg-open", str(gvfs_dir)])
            except Exception as e:
                self.log(f"[ERROR] Could not open MTP: {e}")

        threading.Thread(target=worker, daemon=True).start()

    def start_quick_backup(self):
        backup_dir = Path.home() / "PhoneRescueBackup"
        backup_dir.mkdir(parents=True, exist_ok=True)

        self.bridge.set_backup_ui.emit(True)
        self.log(f"[INFO] Starting backup to: {backup_dir} ...")

        def worker():
            try:
                folders = ["/sdcard/DCIM", "/sdcard/Download", "/sdcard/Documents", "/sdcard/Pictures"]
                for f in folders:
                    name = Path(f).name
                    dest = backup_dir / name
                    self.log(f"[INFO] Pulling {f} -> {dest} ...")
                    subprocess.run(["adb", "pull", f, str(dest)], capture_output=True)
                self.log(f"[SUCCESS] Backup completed. Files saved to: {backup_dir}")
                subprocess.run(["xdg-open", str(backup_dir)])
            except Exception as e:
                self.log(f"[ERROR] Backup failed: {e}")
            finally:
                self.bridge.set_backup_ui.emit(False)

        threading.Thread(target=worker, daemon=True).start()


def main():
    app = QApplication(sys.argv)
    window = ScreenRescueApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
