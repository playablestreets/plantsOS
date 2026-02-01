import time
import board
import busio

import adafruit_ads1x15.ads1015 as ADS1015
import adafruit_ads1x15.ads1x15 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

import adafruit_mpr121


# I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# ADS1015 ADC
ads = ADS1015.ADS1015(i2c)

channels = [
    AnalogIn(ads, ADS.Pin.A0),
    AnalogIn(ads, ADS.Pin.A1),
    AnalogIn(ads, ADS.Pin.A2),
    AnalogIn(ads, ADS.Pin.A3),
]

# MPR121 (default address 0x5A)
mpr1 = adafruit_mpr121.MPR121(i2c)
mpr2 = adafruit_mpr121.MPR121(i2c, address=0x5B)

while True:
    # Read ADC channels
    for i, ch in enumerate(channels):
        print(f"A{i}: raw={ch.value:6d}  voltage={ch.voltage:0.4f} V")

    # Read MPR1 electrode 0
    touched = mpr1.filtered_data(0)
    print(f"MPR 1 E0: {touched:0.4f}")

    # Read MPR1 electrode 0
    touched = mpr2.filtered_data(0)
    print(f"MPR 2 E0: {touched:0.4f}")


    print("-" * 40)
    time.sleep(1)
