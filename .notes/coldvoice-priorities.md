# coldvoice Installation — Immediate Priorities

## Timeline
- Bump-in in a few days

## Hardware
- 2x MPR121 capacitive touch sensors (addresses TBD — likely 0x5A and 0x5B)
- Each MPR121 reads only electrode 0
- Electrodes are conductive tape under ice
- Each MPR121 maps to one audio channel
- MCP2221A USB I2C adapter for laptop dev
- Laptop: macOS running PD with GUI

## Tasks
1. **Laptop dev script (start-laptop.sh)** — run PD + io/main.py on mac via MCP2221A
   - Set BLINKA_MCP2221=1 env var
   - Start io/main.py (background)
   - Start PD with GUI (no jack, no nogui) loading active patch
   - No jackd needed — macOS uses CoreAudio natively in PD
   - May need: pip install adafruit-blinka (check)
2. **Terminal monitor mode** — --monitor flag on io/main.py showing visual bar for electrode 0
3. **MPR121 tuning** — find good threshold/filter settings via PD OSC → io/main.py
   - Had values from ESP32 version but lost them
   - Tuning values set from PD patch as OSC messages
4. **Pure Data sensor interpretation** — user's domain, do not touch .pd files

## Patch restart friction (lower priority)
- /patch command writes active_patch.txt but doesn't properly restart start script

## Future (post-coldvoice)
- Further patch decoupling polish
- Remote SSH tuning/debug tool (visual terminal monitor)
