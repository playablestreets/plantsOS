- run pip install -r ./requirements across python scripts during update
- Broadcast MAC, ip address, and hostname on boot
- set hostname from bopos.devices.csv in helper.py
- add soundcard to bopos.config, read in start.sh

# DECOUPLE BOPOS
- structure below
- hot-swappable patches specified as git repos in bopos.config
  - if patch uses bop, bop can be submodule or flat folder - recursive downloading of bop samplepack not required
- id, position, class, etc specified in bopos.devices.csv

```
bopOS/
  bopos.config 
  bopos.devices.csv 
  DASHBOARD.pd
  DASHBOARD.tosc  
  patches/
    kitechoir/
        bop/
            samplepacks/
                kc_samplepack/
    coldvoice/
    themusicalplants/
  pd/
    bopos.feedback.pd
    bopos.sensors.pd
    bopos.osc.pd
    bopos.gui.pd  
  bash/
    start.sh
    stop.sh
    update.sh
    install.sh
    downloadsamples.sh
    deletesamples.sh
    rc.local
  python/
    helper.py
    io/
        main.py
        io_adc.py
        io_tilt.py
        io_touch.py
        io_screen.py
        io_leds.py
        io_template.py
```
