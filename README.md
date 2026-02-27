# plantsOS

A Raspberry Pi and Pure Data based framework for networked multi-device sound and interactivity. 

- Python provides admin services (updating, rebooting, shutdown), as well as input/output via i2c.   

- Plays well with the [bop](https://github.com/zealtv/bop) library for PD Vanilla. 

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

### login
```
ssh pi@raspberrypi.local
```
### run this one-liner 
```
sudo apt-get update; sudo apt-get upgrade -y; sudo raspi-config nonint do_i2c 0; sudo raspi-config nonint do_expand_rootfs; echo "jackd2 jackd/tweak_rt_limits boolean true" | sudo debconf-set-selections; sudo DEBIAN_FRONTEND=noninteractive apt-get install -y jackd2; sudo apt-get install puredata git pip i2ctools -y; cd ~; python3 -m venv ./venv; git clone https://github.com/playablestreets/plantsOS.git; ~/venv/bin/pip install -r ~/plantsOS/python/requirements.txt; sudo ~/plantsOS/bash/update.sh
```

- pi should copy rc.local and reboot with jack, puredata, io/main.py, and helper.py running
- you may need to edit bash/start.sh to configure soundcard

## Adding custom patches

From DASHBOARD.pd running in puredata on the same network send the following OSC commands

### download patch repo from github and add to the pi
```
/helper addpatch gituser reponame 
```

### switch to patch and reboot
```
/helper patch repo name 
```

### get samples from gdrive if required
```
/helper getsamples 

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
- Issues OS and admin commands like shutdown, update, patch switching, and patch installation.

#### Patch Management via OSC

- `/patch <patchname>`: Switches the active patch (updates `patches/active_patch.txt` and restarts the patch system).
- `/addpatch <user/repo>`: Adds a patch by cloning a GitHub repo (e.g., `user/repo`). If a patch folder of that name exists, it is deleted before cloning. Cloning is recursive (submodules included).

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

- new dashboard (see .notes)
- simplify setup of new devices (incorporate into new dashboard)
- MAC address matching should be case insensitive
- helper.py should just run bash scripts and talk osc
- run pip install -r ./requirements.txt across python scripts during update incase of changes to python libraries (new modules etc)
- Announce MAC, ip address, and hostname on start.
- configure soundcard and jack settings via bopos.config
- the version that gets reported should be a string with an identifier for the patch, followed by a number.  perhaps this can be left to the patch - ie cv99 for coldvoice version 99.  instead of a version perhaps it's a patchID.

- id, hostname, position, class, etc specified in bopos.devices
- set version as shorthand of git commit - perhaps with a tag in the commit comment

```
bopos
├── .claude
│   └── //settings
├── .notes
│   └── //notes, plans, and working memory
├── README.md
├── bash
│   ├── update.sh
│   ├── clearsamples.sh
│   ├── getsamples.sh
│   ├── pull_active_patch.sh
│   ├── rc.local
│   ├── start.sh
│   ├── stop.sh
│   ├── start-laptop.sh
│   ├── stop-laptop.sh
│   ├── restart.sh
│   └── update.sh
├── bopos.devices
├── patches
│   ├── README.md
│   ├── active_patch.txt
│   └── default
│       ├── bopos.config
│       ├── start.sh
|       ├── stop.sh
|       ├── retreive.sh
│       └── main.pd
├── pd
│   ├── bopos.feedback.pd
│   ├── bopos.gui.pd
│   ├── bopos.osc.pd
└── python
    ├── helper.py
    ├── io
    │   ├── README.md
    │   ├── io_ads1015.py
    │   ├── io_ads1115.py
    │   ├── io_lis3dh.py
    │   ├── io_mpr121.py
    │   ├── io_template.py
    │   └── main.py
    └── requirements.txt
```
