# peripheral_adc.py
"""
ADS1015 12-bit Analog-to-Digital Converter

Simple 4-channel ADC for reading analog sensors.
Reads voltages from A0, A1, A2, A3. 
"""

import board
import busio
import adafruit_ads1x15.ads1015 as ADS1015
import adafruit_ads1x15.ads1x15 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

class ADC:
    """
    Simple ADS1015 ADC - reads 4 analog channels.
    """

    def __init__(self, bus=None, address=0x48):
        """
        Setup the ADC.
        
        Args:
            bus: Not used (kept for consistency with other peripherals)
            address: I2C address (usually 0x48)
        """
        self.address = address
        self.name = "adc"
        
        # Will be set in setup()
        self.ads = None
        self.ch0 = None
        self.ch1 = None
        self.ch2 = None
        self.ch3 = None
    
    def setup(self):
        """
        Initialize the hardware.
        """
        # Create I2C connection
        i2c = busio.I2C(board.SCL, board.SDA)
        
        # Create ADS1015 object
        self.ads = ADS1015.ADS1015(i2c, address=self.address)
        
        # Create the 4 channels
        self.ch0 = AnalogIn(self.ads, ADS.Pin.A0)
        self.ch1 = AnalogIn(self.ads, ADS.Pin.A1)
        self.ch2 = AnalogIn(self.ads, ADS.Pin.A2)
        self.ch3 = AnalogIn(self.ads, ADS.Pin.A3)
        
        print(f"{self.name} ready at address 0x{self.address:02X}")
    
    def read_data(self):
        """
        Read all 4 channels.
        
        Returns:
            dict with voltages: {"ch0": 3.3, "ch1": 1.2, ...}
        """
        return {
            "ch0": round(self.ch0.voltage, 3),
            "ch1": round(self.ch1.voltage, 3),
            "ch2": round(self.ch2.voltage, 3),
            "ch3": round(self.ch3.voltage, 3)
        }
    
    def write_data(self, **kwargs):
        """
        Not used - ADC is read-only.
        """
        pass

    def poll(self):
        data = self.read_data()
        return (f"/{self.name}", [data['ch0'], data['ch1'], data['ch2'], data['ch3']])
        pass


    def handle_osc_message(self, path, args):
        """
        Handle OSC commands.
        
        Commands:
            /adc/read - read all channels
            /adc/ch0 - read channel 0 only
            /adc/ch1 - read channel 1 only
            /adc/ch2 - read channel 2 only
            /adc/ch3 - read channel 3 only
        """
        
        # Read all channels
        if path == "/adc/read":
            data = self.read_data()
            # Send back: ch0, ch1, ch2, ch3
            return ("/adc/data", [data['ch0'], data['ch1'], data['ch2'], data['ch3']])
        
        # Read single channels
        elif path == "/adc/ch0":
            return ("/adc/ch0", [round(self.ch0.voltage, 3)])
        
        elif path == "/adc/ch1":
            return ("/adc/ch1", [round(self.ch1.voltage, 3)])
        
        elif path == "/adc/ch2":
            return ("/adc/ch2", [round(self.ch2.voltage, 3)])
        
        elif path == "/adc/ch3":
            return ("/adc/ch3", [round(self.ch3.voltage, 3)])
        
        return None
    
    def cleanup(self):
        """
        Cleanup on shutdown.
        """
        pass