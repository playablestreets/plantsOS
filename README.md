# plantsOS

A Raspberry Pi and Pure Data based framework for networked multi-device sound and interactivity. 

- Python provides admin services (updating, rebooting, shutdown), as well as input/output via i2c.   
- Plays well with the [bop](https://github.com/zealtv/bop) library for PD Vanilla. 

# Requirements 

- Raspberry Pi (any model)

# Installation and Setup

## Flash SD using Raspberry Pi Imager
- Choose OS RASPBERRY PI OS LITE (64-BIT)
- Set username to pi and password
- Set hostname to raspberrypi
- configure wireless network
- enable SSH
- Flash SD

## Install packages
```
# login
ssh pi@raspberrypi.local


# update raspbian
sudo apt-get update; sudo apt-get upgrade -y


# enable i2c and expand filesystem
sudo raspi-config


# install jack2, git, pip, and pure data
sudo apt-get install jackd2 git pip puredata -y

# accept jack realtime priority when prompted 


#make python virtual environment
cd ~
python3 -m venv ./venv


# clone this repo (or your fork)
git clone https://github.com/playablestreets/plantsOS.git


# install python dependencies
~/venv/bin/pip install -r ~/plantsOS/python/requirements.txt


# edit bash/start.sh to configure soundcard
nano ./plantsOS/bash/start.sh


# run update script 
sudo ~/plantsOS/bash/update.sh


# pi should copy rc.local and reboot with jack, puredata, io/main.py, and helper.py running

# if a hostname is linked to your devices MAC address in bopos.local, you can ssh using the new hostname
ssh pi@newhostname.local

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

# FUTURE TODOs

- install script
- Broadcast MAC, ip address, and hostname on boot and on request
- configure soundcard and jack settings via bopos.config
- remove bop from this repo, make bopos.feedback pure pd

## DECOUPLE BOPOS from PD Patch
- structure as below
- hot-swappable patches specified as git repos
- id, hostname, position, class, etc specified in bopos.devices - require a good way of setting this remotely.

```
bopOS/
  bopos.devices
  DASHBOARD.pd
  bash/
    start.sh
    stop.sh
    update.sh
    install.sh
    downloadsamples.sh
    deletesamples.sh
    rc.local
  patches/
    default/
        main.pd
        bopos.config
    active_patch.txt
  pd/
    bop/
    seq/
    bopos.feedback.pd
    bopos.osc.pd
    bopos.gui.pd  
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


