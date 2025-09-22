# robot_utils

Hilfs‑Skripte und Tools für Entwicklung, Flashing und Deployment.

Wichtige Skripte
- scripts/flash_firmware.sh — Wrapper zum Flashen (PlatformIO / picotool)
- scripts/find_serial_port.py — Device discovery helper
- scripts/sync_to_robot.sh — rsync helper / deploy

Usage
- Flash Beispiel:
  ./scripts/flash_firmware.sh --device /dev/ttyACM0 --board robot_pico
- Device find:
  ./scripts/find_serial_port.py --vendor 2e8a

Best Practices
- Skripte idempotent & robust gegenüber fehlenden Geräten schreiben.
- Dokumentiere required host‑tools (picotool, platformio).