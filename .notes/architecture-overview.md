# plantsOS Architecture Notes

## Overview
Raspberry Pi + Pure Data framework for networked multi-device sound installations.

## Core Components
1. **Pure Data (Pd)** - Audio synthesis and OSC routing (bopos.osc.pd, bopos.feedback.pd, bopos.gui.pd)
2. **helper.py** - Admin service: shutdown, reboot, update, patch management (port 7770)
3. **io/main.py** - Sensor bridge: reads I2C peripherals, sends data to Pd via OSC (port 8880)
4. **bash scripts** - Boot, start/stop, update, sample management
5. **DASHBOARD.pd** - Laptop-side admin/control GUI

## OSC Port Map
| Port | Direction | Purpose |
|------|-----------|---------|
| 5550 | Pi → Laptop | Device status/heartbeat broadcast |
| 6660 | Laptop → Pi (broadcast) | Commands to devices |
| 6661 | helper.py → Pd (localhost) | Helper responses |
| 6662 | io/main.py → Pd (localhost) | Sensor data |
| 7770 | Pd → helper.py (localhost) | Admin commands |
| 8880 | Pd → io/main.py (localhost) | I/O commands |

## Boot Sequence
1. rc.local → start.sh (as pi user)
2. start.sh → helper.py (background)
3. start.sh → io/main.py (background)
4. start.sh → jackd audio server
5. start.sh → Pure Data with active patch
6. start.sh → optional patch-specific start.sh

## Patch System
- Patches are git repos stored in patches/
- active_patch.txt holds current patch name
- Each patch has main.pd (entry point), optional bopos.config, optional start.sh
- Patches can be added from GitHub via /addpatch, switched via /patch, updated via /pullpatch

## Supported I2C Peripherals
- ADS1015: 4-channel ADC (analog voltage)
- LIS3DH: 3-axis accelerometer (tilt angles)
- MPR121: 12-channel capacitive touch

## Device Identity
- bopos.devices CSV maps MAC address → hostname, ID, position
- helper.py reads MAC, sets hostname, sends ID to Pd

## Key Dependencies
- jackd2 (audio server)
- Pure Data 0.54+ (audio/OSC processing)
- pyOSC3 (Python OSC)
- Adafruit CircuitPython libraries (sensor drivers)
- bop library (Pd abstractions for synthesis/sequencing)

## README TODO Items (from project)
- Decouple bopos from PD patch
- Hot-swappable patches specified as git repos
- Install script
- Broadcast MAC/IP/hostname on boot
- Configure soundcard/jack via bopos.config
- helper.py should just run bash scripts and talk OSC
