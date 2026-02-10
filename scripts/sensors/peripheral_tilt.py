# peripheral_tilt.py
"""
LIS3DH 3-Axis Accelerometer using PiicoDev library

Reads accelerometer data and outputs tilt values.
Outputs as /tilt with x, y, z values in g-forces.

PiicoDev guide: https://core-electronics.com.au/guides/piicodev-3-axis-accelerometer-lis3dh/
"""

from PiicoDev_LIS3DH import PiicoDev_LIS3DH

class Tilt:
    """
    LIS3DH accelerometer - outputs tilt as x, y, z values.
    """
    
    def __init__(self, bus=None, address=None):
        """
        Initialize the accelerometer.
        
        Args:
            bus: Not used (PiicoDev library handles I2C)
            address: Not used (PiicoDev auto-detects)
        """
        self.name = "tilt"
        
        # Will be set in setup()
        self.motion = None
        
        # Track last values for change detection
        self.last_x = 0
        self.last_y = 0
        self.last_z = 0
    
    def setup(self):
        """
        Initialize the LIS3DH hardware.
        """
        # Create LIS3DH object (auto-detects address)
        self.motion = PiicoDev_LIS3DH()
        
        print(f"{self.name} ready (LIS3DH)")
    
    def read_data(self):
        """
        Read accelerometer x, y, z values.
        
        Returns:
            dict: {"x": 0.0, "y": 0.0, "z": 1.0}
                  Values in g-forces (-1 to +1 typically)
                  z ≈ 1.0 when flat, x/y change with tilt
        """
        # Get acceleration in g
        accel = self.motion.acceleration
        
        return {
            "x": round(accel['x'], 3),
            "y": round(accel['y'], 3),
            "z": round(accel['z'], 3)
        }
    
    def write_data(self, **kwargs):
        """
        Not used - accelerometer is read-only.
        """
        pass
    
    def poll(self):
        """
        Auto-send tilt data.
        
        Returns tilt as /tilt x y z
        """
        data = self.read_data()
        return (f"/{self.name}", [data['x'], data['y'], data['z']])
    
    def handle_osc_message(self, path, args):
        """
        Handle OSC messages for tilt sensor.
        
        Commands:
            /tilt/read - Read current tilt values
            /tilt/x - Read x-axis only
            /tilt/y - Read y-axis only
            /tilt/z - Read z-axis only
        """
        
        # Read all axes
        if path == "/tilt/read":
            data = self.read_data()
            return ("/tilt", [data['x'], data['y'], data['z']])
        
        # Read individual axes
        elif path == "/tilt/x":
            data = self.read_data()
            return ("/tilt/x", [data['x']])
        
        elif path == "/tilt/y":
            data = self.read_data()
            return ("/tilt/y", [data['y']])
        
        elif path == "/tilt/z":
            data = self.read_data()
            return ("/tilt/z", [data['z']])
        
        return None
    
    def cleanup(self):
        """
        Cleanup on shutdown.
        """
        print(f"{self.name} shutting down")
        pass