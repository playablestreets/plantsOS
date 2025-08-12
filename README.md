# plantsOS

A Raspberry Pi and Arduino based framework for networked multi-device sound and interactivity.   This repo provides scaffolding for the [bop](https://github.com/zealtv/bop) library for PD Vanilla. Python provide admin services (updating, rebooting, shutdown). 

# Requirements 

- puredata 0.54 vanilla 
- python3
- [pyOSC3](https://pypi.org/project/pyOSC3/)


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
./venv/bin/pip install pyOSC3

```

## Install project code
```
# goto home directory
cd ~


# clone this repo (or your fork)
git clone https://github.com/playablestreets/plantsOS.git


# !copy samples
# !edit scripts/start.sh to configure soundcard


# run update script 
sudo ~/plantsOS/scripts/update.sh


# pi should copy rc.local and reboot with jack, puredata, and helper.py running

```
