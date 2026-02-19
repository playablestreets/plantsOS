# plantsOS

A Raspberry Pi and Pure Data based framework for networked multi-device sound and interactivity. 

- Python provides admin services (updating, rebooting, shutdown), as well as input/output via i2c.   
- Plays well with the [bop](https://github.com/zealtv/bop) library for PD Vanilla. 

# Requirements 

- Raspberry Pi (any model)

# Installation and Setup

Flash SD using Raspberry Pi Imager
- Choose OS RASPBERRY PI OS LITE (64-BIT)
- Set username to pi and password
- Set hostname to raspberrypi
- configure wireless network
- enable SSH
- Flash SD


Boot pi and login
```
ssh pi@raspberrypi.local
```

use raspi-config to enable i2c and expand filesystem
```
sudo raspi-config
```

Install packages  ( accept jack realtime priority when prompted )
```
sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get install -y jackd2 git python3-pip puredata python3-venv && cd ~ && python3 -m venv ./venv && git clone https://github.com/playablestreets/plantsOS.git && ~/venv/bin/pip install -r ~/plantsOS/python/requirements.txt
```

edit bash/start.sh to configure soundcard
```
nano ./plantsOS/bash/start.sh
```

run update script 
```
sudo ~/plantsOS/bash/update.sh
```

pi should reboot with jack, puredata, and python running

# Multidevice Network (bopos.devices)
For spatial or multidevice setups, the bopos.devices file specifies devices running on your network.  Devices are identified by MAC address (lowercase) and you can a hostname as well as these variables which will be passed Pure Data:
- Device ID
- position of left element
- position of right element


# OSC architecture

## MAIN.pd 
### Listening on 6660, 6661, 6662
- Runs on Pis. 
- Generates audio in response to incoming sensor data.


### Broadcasts to 5550
    report to ADMIN.pd

### Unicasts to localhost:7770
    send to helper.py
    forward 6660:/helper/* to helper.py (localhost:7770)


### Unicasts to localhost:8880
    send to io/main.py
    forward 6660:/io/* to io/main.py (localhost:8880)


## ADMIN.pd
### Listening on 5550

- Runs on laptop.
- Provides monitor and control of Pis.

### Broadcasts to 6660
    Send to MAIN.pd

### Broadcasts to 7770
    Send to io/main.py

## helper.py
### Listening 7770

- Runs on Pis. 
- Issues OS and admin commands like shutdown and update.

### Unicasts to localhost:6661
    Send to MAIN.pd

## io/main.py 
### Listening 8880

- Runs on Pis. 
- Reads/writes to/from sensors and i2c peripherals.

### Unicasts to localhost:6662
    Send to MAIN.pd

---

# TODO

- document osc commands and return values and ranges in io_modules - normalise where sensible
- Broadcast MAC, ip address, and hostname on boot and on request
- configure soundcard and jack settings in a config file
- remove bop from this repo, make bopos.feedback pure pd
- bopos.devices should be json and allow for arbitrary properties to be passed to PD. Find a good way to manage this.
- rename update.sh to updateOS.sh, create scripts to add and update patch repos
- add osc commands for the scripts above as well as setting active patch
- a mechanism for persistance - send an osc message to a script which stores value in json.  those values are returned at boot.

