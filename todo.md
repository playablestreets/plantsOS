- run pip install -r ./requirements across python scripts during update
- Broadcast MAC, ip address, and hostname on boot
- set hostname on start from helper.py

# architechture and python io management
```
- sends a single osc bundle with all sensor data
- one message to control polling rate
- super simple - sleep in main()

PD can create peripherals (name, type, i2c_address)
/io/create adc1 ads1015 0x48
/io/create adc2 ads1015 0x4c
/io/create tilt lis3dh 0x19
adds the device to the list of peripherals and starts polling it at the next poll cycle

Once created, modules can be polled 
/poll 10  (poll all modules at 10 Hz)

returns a single osc bundle with all incoming data from modules
/adc1/data 3.3 1.2 0.0 0
/tilt/data 0.1 0.5 0.0
/touch/data 0 1 0

modules can be sent commands
/touch/sensitivity 0.9
/screen/line1 "Hello world"
/leds/rgb 255 0 128

That might decouple the python code from the pd patch and allow 
for a  structure like so:
bopOS/
  bopos.config # feeds bash scripts
  bopos.devices.csv # 
  patches/
    kitechoir/
    coldvoice/
    themusicalplants/
  pd/
    bopos.feedback.pd
    bopos.sensors.pd
    bopos.osc.pd
    bopos.gui.pd
    DASHBOARD.pd
  scripts/
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
the folders in patches are independant repos with their own pd patches.
these can use but don't require bop.
```