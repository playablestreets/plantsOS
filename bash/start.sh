#!/bin/bash

#1.) get list of available soundcards by running: cat /proc/asound/cards
#2.) edit the SOUNDCARD variable below as needed

#SOUNDCARD="YOUR_SOUNDCARD"
# SOUNDCARD="sndrpihifiberry"
# SOUNDCARD="IQaudIODAC"
SOUNDCARD="DigiAMP"

RND=$RANDOM
MACADDRESS=$(cat /sys/class/net/wlan0/address)
# MACADDRESS=$(cat /sys/class/net/eth0/address)
now=$(date --iso-8601=seconds)
STARTDATE=$(date -d "$now" +%Y%m%d)
STARTTIME=$(date -d "$now" +%H%M%S)

echo "------------------- Waiting..."

sleep 15

echo "------------------- Starting bopOS..."
echo "SOUNDCARD: $SOUNDCARD"
echo "MAC ADDRESS: $MACADDRESS"
echo "RANDOM: $RND"
echo "STARTDATE: $STARTDATE"
echo "STARTTIME: $STARTTIME"


#Start Jack 
echo "------------------- Starting Jack..."
jackd -P70 -p16 -t2000 -d alsa -dhw:$SOUNDCARD -p 512 -n 2 -r 44100 -s -P& #44.1khz        
# jackd -P80 -t2000 -d alsa -dhw:$SOUNDCARD -p 1024 -n 2 -r 22050 -s -P& #22khz

# leave enough time for jack to start before launching PD
sleep 15

echo "------------------- Starting helper.py..."
# PYTHON
sudo /home/pi/venv/bin/python /home/pi/plantsOS/python/helper.py $MACADDRESS &

echo "------------------- Starting bopOS IO..."
sudo /home/pi/venv/bin/python /home/pi/plantsOS/python/io/main.py &

sleep 1

# Determine active patch
ACTIVE_PATCH=$(cat /home/pi/plantsOS/patches/active_patch.txt)
PATCH_PATH="/home/pi/plantsOS/patches/$ACTIVE_PATCH"
PATCH_ENTRYPOINT="$PATCH_PATH/main.pd"

echo "------------------- Starting Pure Data..."
# PUREDATA
pd -nogui -jack -open "$PATCH_ENTRYPOINT" -send "; RANDOM $RND; STARTTIME $STARTTIME; STARTDATE $STARTDATE; " &

exit