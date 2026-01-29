import time
import board
import busio

import adafruit_ads1x15.ads1015 as ADS1015
import adafruit_ads1x15.ads1x15 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


# import board
# i2c = board.I2C()

# I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# ADC instance
ads = ADS1015.ADS1015(i2c)


channels = [
    AnalogIn(ads, ADS.Pin.A0),
    AnalogIn(ads, ADS.Pin.A1),
    AnalogIn(ads, ADS.Pin.A2),
    AnalogIn(ads, ADS.Pin.A3),
]

while True:
    for i, ch in enumerate(channels):
        print(f"A{i}: raw={ch.value:6d}  voltage={ch.voltage:0.4f} V")
    print("-" * 40)
    time.sleep(1)
