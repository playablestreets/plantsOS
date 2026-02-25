# coldvoice Installation — Immediate Priorities

## Timeline
- Bump-in in a few days

## Tasks
1. **MPR121 tuning** — find good touch/release thresholds and filter settings
   - Had values from ESP32 version but lost them
   - Need low-friction way to iterate on settings
2. **Pure Data sensor interpretation** — user's domain, do not touch .pd files
3. **Patch restart friction** — /patch command doesn't properly restart start script

## Future (post-coldvoice)
- Laptop dev script: runs pd + io/main.py with MCP2221A USB I2C adapter
- Further patch decoupling polish

## Hardware for coldvoice
- MPR121 capacitive touch (12 channels)
- Likely ADS1015 ADC as well (from default patch)
- Unknown: how many Pis, which sensors on which devices
