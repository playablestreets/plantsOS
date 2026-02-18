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
~/venv/bin/pip install -r ~/plantsOS/python/requirements.txt




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

# FUTURE TODOs

- install script
- Broadcast MAC, ip address, and hostname on boot and on request
- configure soundcard and jack settings via bopos.config
- look first in active patch for bopos.config and bopos.devices (?)

## DECOUPLE BOPOS from PD Patch
- structure as below
- hot-swappable patches specified as git repos
- id, hostname, position, class, etc specified in bopos.devices - require a good way of setting this remotely.

```
bopOS/
  bopos.devices
  DASHBOARD.pd
  DASHBOARD.tosc  
  patches/
    patches.json
    .active_patch.txt
  pd/
    bop/
    seq/
    bopos.feedback.pd
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


# Decoupling Plan

## Plan: Decoupled Patch Management with jq-based Metadata Access

This plan enables hot-swappable, repo-based Pure Data patches with simple, maintainable selection and management, using jq for JSON parsing in shell scripts.

---

**Steps**

1. **Patch Registry**
   - Create [patches/patches.json](patches/patches.json) as a JSON array.
   - Each entry includes:
     - `name` (unique, used for selection)
     - `git_url` (required)
     - `samplepacks_url` (optional)
     - `entrypoint` (optional, defaults to `main.pd`)
   - Example:
     ```json
     [
       {
         "name": "kitechoir",
         "git_url": "https://github.com/yourorg/kitechoir-patch.git",
         "samplepack_url": "https://drive.google.com/uc?export=download&id=xxxx",
         "entrypoint": "MAIN.pd"
       },
       {
         "name": "coldvoice",
         "git_url": "https://github.com/yourorg/coldvoice-patch.git"
       }
     ]
     ```

2. **Active Patch Selection**
   - Store the name of the active patch in [patches/active_patch.txt](patches/active_patch.txt).
   - Only the patch name (e.g., `kitechoir`) is stored, one per line.
   - Update this file via OSC handler in [python/helper.py](python/helper.py) or manually.

3. **Patch Cloning & Launch Logic in start.sh**
   - Ensure jq is installed (`sudo apt-get install jq`).
   - In [bash/start.sh](bash/start.sh):
     - Read the active patch name:
       ```sh
       ACTIVE_PATCH=$(cat patches/active_patch.txt)
       ```
     - Extract patch metadata using jq:
       ```sh
       PATCH_INFO=$(jq -r --arg name "$ACTIVE_PATCH" '.[] | select(.name == $name)' patches/patches.json)
       GIT_URL=$(echo "$PATCH_INFO" | jq -r '.git_url')
       ENTRYPOINT=$(echo "$PATCH_INFO" | jq -r '.entrypoint // "main.pd"')
       SAMPLEPACKS_URL=$(echo "$PATCH_INFO" | jq -r '.samplepacks_url // empty')
       ```
     - If the patch folder is missing, clone it:
       ```sh
       if [ ! -d "patches/$ACTIVE_PATCH" ]; then
         git clone "$GIT_URL" "patches/$ACTIVE_PATCH"
       fi
       ```
     - Download samplepack if `SAMPLEPACKS_URL` is set.
     - Launch the patch’s entrypoint:
       ```sh
       pd "patches/$ACTIVE_PATCH/$ENTRYPOINT"
       ```

4. **OSC Patch Switching**
   - Add OSC handler in [python/helper.py](http://_vscodecontentref_/0) (e.g., `/setpatch kitechoir`).
   - Handler updates .active_patch.txt and triggers a restart or patch reload.

5. **Documentation**
   - Update [README.md](http://_vscodecontentref_/1) to explain:
     - The patch system and file formats.
     - How to add/switch patches.
     - The jq dependency and installation.

---

**Verification**
- Add two patches to patches.json, one with all fields, one with only required.
- Switch patches by editing active_patch.txt and via OSC.
- Confirm correct repo, samplepack, and entrypoint are used.
- Confirm fallback to `main.pd` when `entrypoint` is omitted.

**Decisions**
- Use patches/active_patch.txt for active patch selection.
- Use patches/patches.json for patch metadata only.
- Use jq in start.sh for robust, maintainable JSON parsing.
- Default entrypoint to `main.pd` if not specified.