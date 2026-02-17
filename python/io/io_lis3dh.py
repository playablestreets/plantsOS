# peripheral_tilt.py
"""
LIS3DH 3-Axis Accelerometer
Reads tilt/acceleration in x, y, z axes
Addresses:
    0x19 (Default)
    0x18 (Selectable via a solder bridge on the hardware module)
"""

from PiicoDev_LIS3DH import PiicoDev_LIS3DH

class IO_LIS3DH:
    """LIS3DH accelerometer - outputs x, y, z acceleration in g-forces."""
    
    def __init__(self, bus=None, address=None):
        self.name = "tilt"
        self.motion = None
        self.bus = bus
        self.address = address
    
    def setup(self):
        """Initialize the LIS3DH hardware."""
        init_kwargs = {}
        if self.bus is not None:
            init_kwargs['bus'] = self.bus
        if self.address is not None:
            init_kwargs['addr'] = self.address
        self.motion = PiicoDev_LIS3DH(**init_kwargs)
        print(f"  {self.name}: 3-axis accelerometer ready")
    
    def read_data(self):
        """
        Read acceleration on all 3 axes.
        Returns: [x, y, z] in g-forces
        """
        accel = self.motion.acceleration
        return [
            round(accel['x'], 3),
            round(accel['y'], 3),
            round(accel['z'], 3)
        ]
    
    def write_data(self, **kwargs):
        """Accelerometer is read-only."""
        pass
    
    def cleanup(self):
        """Cleanup on shutdown."""
        pass
