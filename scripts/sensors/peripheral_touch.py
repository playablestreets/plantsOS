# peripherals/touch.py
"""
MPR121 Capacitive Touch Sensor - Filtered Data

12-channel capacitive touch sensor.
Reads filtered capacitance values (0-1023) instead of just touch/no-touch.
Great for continuous sensing, proximity detection, and plant monitoring.

Adafruit guide: https://learn.adafruit.com/adafruit-mpr121-12-key-capacitive-touch-sensor-breakout-tutorial
"""

import board
import busio
import adafruit_mpr121

class Touch:
    """
    MPR121 capacitive sensor - reads filtered analog values.
    
    Returns continuous values (0-1023) showing capacitance level,
    not just binary touch states.
    """
    
    def __init__(self, bus=None, address=0x5A):
        """
        Initialize the touch sensor.
        
        Args:
            bus: Not used (Adafruit library handles I2C)
            address: I2C address (default 0x5A, can be 0x5B, 0x5C, 0x5D)
        """
        self.address = address
        self.name = "touch"
        
        # Will be set in setup()
        self.mpr121 = None
        
        # Number of electrodes (0-11)
        self.num_electrodes = 12
    
    def setup(self):
        """
        Initialize the MPR121 hardware.
        """
        # Create I2C connection
        i2c = busio.I2C(board.SCL, board.SDA)
        
        # Create MPR121 object
        self.mpr121 = adafruit_mpr121.MPR121(i2c, address=self.address)
        
        print(f"{self.name} ready at address 0x{self.address:02X}")
        print(f"  Default touch threshold: 12")
        print(f"  Default release threshold: 6")
    
    def read_data(self):
        """
        Read filtered capacitance data from all electrodes.
        
        Returns:
            dict: {"ch0": 512, "ch1": 234, ..., "ch11": 678}
                  Values range from 0-1023
                  Higher values = more capacitance/closer proximity
        """
        data = {}
        
        for i in range(self.num_electrodes):
            # Read filtered data (0-1023)
            filtered_value = self.mpr121.filtered_data(i)
            data[f"ch{i}"] = filtered_value
        
        return data
    
    def read_channel(self, channel_num):
        """
        Read filtered data from a specific channel.
        
        Args:
            channel_num: Channel number (0-11)
            
        Returns:
            int: Filtered value (0-1023)
        """
        if 0 <= channel_num < self.num_electrodes:
            return self.mpr121.filtered_data(channel_num)
        return 0
    
    def read_baseline(self, channel_num):
        """
        Read baseline (calibration) value for a channel.
        
        The baseline is what the sensor reads when nothing is touching.
        Compare filtered_data to baseline to detect changes.
        
        Args:
            channel_num: Channel number (0-11)
            
        Returns:
            int: Baseline value
        """
        if 0 <= channel_num < self.num_electrodes:
            return self.mpr121.baseline_data(channel_num)
        return 0
    
    def write_data(self, **kwargs):
        """
        Configure touch sensor settings.
        
        Args:
            touch_threshold: Touch detection threshold (0-255, default 12)
            release_threshold: Release detection threshold (0-255, default 6)
        
        Note: Lower touch_threshold = triggers easier
              Higher values = need stronger touch
        """
        if 'touch_threshold' in kwargs and 'release_threshold' in kwargs:
            touch = int(kwargs['touch_threshold'])
            release = int(kwargs['release_threshold'])
            self.mpr121.set_thresholds(touch, release)
            print(f"Thresholds: touch={touch}, release={release}")
    
    def handle_osc_message(self, path, args):
        """
        Handle OSC messages for filtered capacitance data.
        
        Commands:
            /touch/read - Read all 12 channels (filtered values)
            /touch/ch0 through /touch/ch11 - Read specific channel
            /touch/baseline/0 through /touch/baseline/11 - Read baseline
            /touch/threshold [touch] [release] - Set thresholds
            /touch/info - Get number of channels
        
        Returns:
            tuple: (osc_path, osc_args) or None
        """
        
        # Read all channels (filtered data)
        if path == "/touch/read":
            data = self.read_data()
            # Send back all 12 values
            values = [data[f"ch{i}"] for i in range(self.num_electrodes)]
            return ("/touch/data", values)
        
        # Read specific channel
        elif path.startswith("/touch/ch"):
            try:
                # Extract channel from /touch/ch0, /touch/ch1, etc.
                channel_num = int(path.split("ch")[-1])
                if 0 <= channel_num < self.num_electrodes:
                    value = self.read_channel(channel_num)
                    return (f"/touch/ch{channel_num}", [value])
            except (ValueError, IndexError):
                pass
        
        # Read baseline for specific channel
        elif path.startswith("/touch/baseline/"):
            try:
                channel_num = int(path.split("/")[-1])
                if 0 <= channel_num < self.num_electrodes:
                    baseline = self.read_baseline(channel_num)
                    return (f"/touch/baseline/{channel_num}", [baseline])
            except (ValueError, IndexError):
                pass
        
        # Set touch and release thresholds
        elif path == "/touch/threshold":
            if len(args) >= 2:
                touch_thresh = int(args[0])
                release_thresh = int(args[1])
                self.write_data(
                    touch_threshold=touch_thresh,
                    release_threshold=release_thresh
                )
                return ("/touch/status", ["thresholds_set"])
        
        # Get sensor info
        elif path == "/touch/info":
            return ("/touch/info", [self.num_electrodes])
        
        return None
    
    def cleanup(self):
        """
        Cleanup on shutdown.
        """
        print(f"{self.name} shutting down")
        pass