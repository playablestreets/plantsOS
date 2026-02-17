# plantsOS

A Raspberry Pi and Pure Data based framework for networked multi-device sound and interactivity. 

Python provide admin services (updating, rebooting, shutdown), as well as input/output via i2c.   

Plays well with the [bop](https://github.com/zealtv/bop) library for PD Vanilla. 

# Requirements 

- Raspberry Pi (any model)

# Installation and Setup

## Flash SD using Raspberry Pi Imager
- Choose OS RASPBERRY PI OS LITE (64-BIT)
- Set username and password
- configure wireless LAN
- enable SSH
- Flash SD

## Install packages
```
# login
ssh pi@raspberrypi.local


# update
sudo apt-get update
sudo apt-get upgrade


# enable i2c, expand filesystem, and set gpu memory to 16 (if applicable)
sudo raspi-config


# install jack2
sudo apt-get install jackd2


# install git
sudo apt-get install git


# install pure-data dependencies
sudo apt-get install build-essential automake autoconf libtool gettext libasound2-dev libjack-jackd2-dev tcl tk wish


# build and install puredata 0.54+
cd ~
git clone https://github.com/pure-data/pure-data.git
cd ./pure-data/
./autogen.sh
./configure --enable-jack
make
sudo make install


#install pip
sudo apt-get install pip


#make python virtual environment
cd ~
python3 -m venv ./venv


# install python dependencies
./venv/bin/pip install pyOSC3 piicodev gdown adafruit-blinka adafruit-circuitpython-ads1x15


```

## Install project code
```
# goto home directory
cd ~


# clone this repo (or your fork)
git clone https://github.com/playablestreets/plantsOS.git


# !copy samples
# !edit bash/start.sh to configure soundcard


# run update script 
sudo ~/plantsOS/bash/update.sh


# pi should copy rc.local and reboot with jack, puredata, io/main.py, and helper.py running

```

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

- run pip install -r ./requirements across python scripts during update
- Broadcast MAC, ip address, and hostname on boot
- add soundcard to bopos.config, read in start.sh

## DECOUPLE BOPOS
- structure as below
- hot-swappable patches specified as git repos in bopos.config
  - if patch uses bop, bop can be submodule or flat folder  (recursive downloading of bop or samplepacks not required)
- id, hostname, position, class, etc specified in bopos.devices

```
bopOS/
  bopos.config 
  bopos.devices
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
