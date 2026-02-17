# peripheral_touch.py
"""
MPR121 Capacitive Touch Sensor
12-channel capacitive touch sensor with filtered data (0-1023)
"""

import board
import busio
import adafruit_mpr121

class Touch:
    """MPR121 capacitive sensor - reads filtered analog values from 12 electrodes."""
    
    def __init__(self, bus=None, address=0x5A):
        self.address = address
        self.name = "touch"
        self.mpr121 = None
        self.num_electrodes = 12
    
    def setup(self):
        """Initialize the MPR121 hardware."""
        i2c = busio.I2C(board.SCL, board.SDA)
        self.mpr121 = adafruit_mpr121.MPR121(i2c, address=self.address)
        print(f"  {self.name}: 12-channel capacitive touch ready")
    
    def read_data(self):
        """
        Read filtered capacitance from all 12 electrodes.
        Returns: [ch0, ch1, ch2, ..., ch11] values 0-1023
        Higher values = more capacitance/closer proximity
        """
        return [self.mpr121.filtered_data(i) for i in range(self.num_electrodes)]
    
    def write_data(self, **kwargs):
        """
        Configure touch sensor settings.
        Expects kwargs['command'] and kwargs['args']
        
        Commands:
            threshold: Set touch/release thresholds
                       args: [touch_threshold, release_threshold]
        """
        command = kwargs.get('command', '')
        args = kwargs.get('args', [])
        
        if command == 'threshold' and len(args) >= 2:
            touch = int(args[0])
            release = int(args[1])
            self.mpr121.set_thresholds(touch, release)
            print(f"  {self.name}: thresholds set to touch={touch}, release={release}")
    
    def cleanup(self):
        """Cleanup on shutdown."""
        pass
