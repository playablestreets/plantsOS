from time import sleep
from pyOSC3 import OSCServer, OSCClient, OSCMessage
import board
import busio

import adafruit_ads1x15.ads1015 as ADS1015
import adafruit_ads1x15.ads1x15 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

import adafruit_mpr121

# Set up the OSC client
client = OSCClient()
client.connect( ('127.0.0.1', 9990) )

# I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# ADS1015 ADC
adc = ADS1015.ADS1015(i2c)

channels = [
    AnalogIn(adc, ADS.Pin.A0),
    AnalogIn(adc, ADS.Pin.A1),
    AnalogIn(adc, ADS.Pin.A2),
    AnalogIn(adc, ADS.Pin.A3),
]

# MPR121 (default address 0x5A)
mpr1 = adafruit_mpr121.MPR121(i2c, address=0x5A) 
mpr2 = adafruit_mpr121.MPR121(i2c, address=0x5C)

while True:
    # Read ADC channels
    for i, ch in enumerate(channels):
        print(f"A{i}: raw={ch.value:6d}  voltage={ch.voltage:0.4f} V")

    msg_touch = OSCMessage("/touch")

    # Read MPR1 electrode 0
    touched = mpr1.filtered_data(0)
    print(f"MPR 1 E0: {touched:0.4f}")
    msg_touch.append(float(touched), 'f')

    # Read MPR1 electrode 0
    touched = mpr2.filtered_data(0)
    print(f"MPR 2 E0: {touched:0.4f}")
    msg_touch.append(float(touched), 'f')

    client.send(msg_touch)

    print("-" * 40)
    sleep(1)
