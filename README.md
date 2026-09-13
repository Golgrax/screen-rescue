# ScreenRescue

Android Device Recovery, Screen Mirroring, and Automation Utility for Linux.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: Linux](https://img.shields.io/badge/Platform-Linux-blue.svg)](https://kernel.org)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-brightgreen.svg)](https://python.org)
[![scrcpy](https://img.shields.io/badge/scrcpy-v2.0+-orange.svg)](https://github.com/Genymobile/scrcpy)

---

## Overview

ScreenRescue is a Linux desktop utility for interacting with Android devices that have damaged displays, unresponsive touch digitizers, or malfunctioning physical buttons.

The application integrates `scrcpy` and `adb` to provide display mirroring with physical digitizer suppression, automated lockscreen credential entry, ADB authorization bypass, and local data extraction.

---

## Features

### Display Mirroring and Digitizer Suppression
- Streams display output via `scrcpy` while powering off the physical panel (`-S`).
- Suppresses erratic capacitive touches and hardware driver mistouch interrupts (`KEY_MISTAKEN_TOUCH` / keycode 251) caused by cracked glass or moisture.
- Provides a keyboard shortcut (`Alt + O`) to toggle the physical display state during an active session.

### Automated Blind Unlock
- **PIN:** Submits individual hardware keycodes (`KEYCODE_0` through `KEYCODE_9`) with defined timing delays to reliably authenticate on Android 15 secure lockscreen bouncers (`FLAG_SECURE`).
- **Password:** Submits alphanumeric credentials via ADB or USB HID keystrokes.
- **Pattern:** Translates 3x3 pattern sequences into screen-scaled touch drag coordinates.
- **OTG Keyboard Fallback:** Emulates a USB HID keyboard via `scrcpy --otg --mouse=disabled` for devices where ADB is unauthorized or unavailable.

### Power and Timeout Configuration
- Applies Android configuration overrides (`svc power stayon true`, `stay_on_while_plugged_in = 7`, `power_button_instantly_locks = 0`, `end_button_behavior = 1`) to prevent hardware button shorts from putting the device to sleep.
- Includes an optional keep-awake monitor thread that checks device power states and sends wakeup events (`KEYCODE_WAKEUP`) if sleep is detected.

### Credential Removal
- Provides direct removal of device credentials via `locksettings clear --old <credential>` and `locksettings set-disabled true` to eliminate recurring lockouts during recovery.

### ADB Authorization Helper
- Automates USB debugging authorization approval on unauthorized devices by sending keyboard navigation sequences (`Tab -> Tab -> Right -> Enter`) over USB OTG.

### File Extraction
- Accesses internal shared storage via GVFS MTP.
- Performs automated local backup of standard storage directories (`DCIM`, `Download`, `Documents`, `Pictures`) using ADB pull.

---

## Technical Details

| Subsystem | Behavior |
| :--- | :--- |
| **USB Protocol Handling** | Certain chipsets (such as Unisoc/Spreadtrum) encounter kernel pipe errors when initializing USB mouse endpoints. ScreenRescue runs OTG sessions with mouse input disabled to maintain reliable HID keyboard communication. |
| **Digitizer Isolation** | Turning off the physical display panel disables the capacitive touch controller at the hardware level. Scrcpy continues reading from SurfaceFlinger/GPU compositor buffers without interference from ghost touch events. |
| **Android 15 Bouncer Input** | Android 15 drops synthetic text input on secure lock surfaces. Numeric PIN submission is handled by dispatching individual hardware keycodes with defined timing intervals. |

---

## Prerequisites

The following dependencies are required:
- Python 3.10 or higher
- `scrcpy` (version 2.0 or higher)
- `adb` (`android-tools-adb`)
- `xdotool`

---

## Installation and Execution

### AppImage (Recommended)

Download the precompiled x86_64 AppImage from the [Releases](https://github.com/Golgrax/screen-rescue/releases) page:

```bash
chmod +x ScreenRescue-x86_64.AppImage
./ScreenRescue-x86_64.AppImage
```

### Running from Source

```bash
git clone https://github.com/Golgrax/screen-rescue.git
cd screen-rescue
pip install -r requirements.txt
python3 main.py
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
