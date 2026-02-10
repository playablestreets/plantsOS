# peripherals/template.py
"""
Template for creating new I2C peripheral modules.

Copy this file and rename it to match your device (e.g., 'led_matrix.py')
Then fill in the methods below with your device-specific code.
"""

class PeripheralTemplate:
    """
    Template class for I2C peripherals.
    
    Replace 'PeripheralTemplate' with your device name (e.g., 'LEDMatrix').
    """
    
    def __init__(self, bus, address=0x00):
        """
        Initialize the peripheral.
        
        Args:
            bus: The smbus2.SMBus object for I2C communication
            address: The I2C address of your device (find this in the datasheet)
        """
        self.bus = bus
        self.address = address
        
        # This name is used in OSC paths, e.g., "/mydevice/read"
        # Keep it short and descriptive
        self.name = "mydevice"
        
        # Add any variables to track device state here
        self.is_ready = False
        self.last_value = 0
    
    def setup(self):
        """
        Initialize the hardware - called once at startup.
        
        This is where you:
        - Write configuration to I2C registers
        - Set device modes or settings
        - Perform calibration
        
        If your device doesn't need setup, just leave this with 'pass'.
        """
        # Example: Wake up the device by writing to a power register
        # self.bus.write_byte_data(self.address, 0x6B, 0x00)
        
        # Example: Configure a mode register
        # self.bus.write_byte_data(self.address, 0x1A, 0x03)
        
        self.is_ready = True
        print(f"{self.name} initialized at address 0x{self.address:02X}")
    
    def read_data(self):
        """
        Read current values from the device.
        
        Returns:
            dict: A dictionary with named values, e.g., {"value": 123, "status": "ok"}
        
        This method is called when you want to poll the device or when
        Pure Data requests data via OSC.
        """
        # Example: Read a single byte from register 0x00
        # value = self.bus.read_byte_data(self.address, 0x00)
        
        # Example: Read a 16-bit value (word) from register 0x00
        # value = self.bus.read_word_data(self.address, 0x00)
        
        # Example: Read multiple bytes starting at register 0x00
        # data = self.bus.read_i2c_block_data(self.address, 0x00, 6)
        # x = data[0]
        # y = data[1]
        # z = data[2]
        
        # Return your data as a dictionary
        return {
            "value": 0,
            "status": "ok"
        }
    
    def write_data(self, **kwargs):
        """
        Write values to the device.
        
        Args:
            **kwargs: Named parameters for values to write
                     (e.g., brightness=128, mode=3)
        
        This is called when Pure Data sends commands via OSC.
        """
        # Example: Set brightness
        # if 'brightness' in kwargs:
        #     brightness = kwargs['brightness']
        #     self.bus.write_byte_data(self.address, 0x10, brightness)
        
        # Example: Set multiple values
        # if 'red' in kwargs and 'green' in kwargs and 'blue' in kwargs:
        #     colors = [kwargs['red'], kwargs['green'], kwargs['blue']]
        #     self.bus.write_i2c_block_data(self.address, 0x00, colors)
        
        pass
    
    def handle_osc_message(self, path, args):
        """
        Handle incoming OSC messages for this device.
        
        Args:
            path: The OSC path (e.g., "/mydevice/read")
            args: List of arguments sent with the message
        
        Returns:
            tuple: (osc_path, osc_args) to send back to Pure Data, or None
        
        Define all the OSC commands your device responds to here.
        Common patterns:
        - /{name}/read - read and return current values
        - /{name}/set - write a value to the device
        - /{name}/status - return device status
        """
        
        # Command: Read data from device
        if path == f"/{self.name}/read":
            data = self.read_data()
            # Send back the value to Pure Data
            return (f"/{self.name}/data", [data['value']])
        
        # Command: Write a single value (expects one argument)
        elif path == f"/{self.name}/set":
            if len(args) > 0:
                value = args[0]
                self.write_data(value=value)
                return (f"/{self.name}/status", ["ok"])
        
        # Command: Write multiple values (expects multiple arguments)
        elif path == f"/{self.name}/rgb":
            if len(args) >= 3:
                r, g, b = args[0], args[1], args[2]
                self.write_data(red=r, green=g, blue=b)
                return (f"/{self.name}/status", ["color_set"])
        
        # Command: Get device status
        elif path == f"/{self.name}/status":
            status = "ready" if self.is_ready else "not_ready"
            return (f"/{self.name}/status", [status])
        
        # If this device doesn't handle this OSC path, return None
        return None
    
    def cleanup(self):
        """
        Clean up when shutting down (optional).
        
        Use this to:
        - Turn off LEDs
        - Put device in low power mode
        - Close connections
        
        If you don't need cleanup, just leave this with 'pass'.
        """
        # Example: Turn off all outputs
        # self.bus.write_byte_data(self.address, 0x00, 0x00)
        
        pass


# Example of a real implementation:
# 
# class TemperatureSensor:
#     def __init__(self, bus, address=0x48):
#         self.bus = bus
#         self.address = address
#         self.name = "temp"
#     
#     def setup(self):
#         pass  # TMP102 doesn't need setup
#     
#     def read_data(self):
#         raw = self.bus.read_word_data(self.address, 0x00)
#         # Swap bytes (I2C returns big-endian)
#         raw = ((raw & 0xFF) << 8) | ((raw & 0xFF00) >> 8)
#         # Convert to celsius (12-bit mode)
#         celsius = (raw >> 4) * 0.0625
#         return {"celsius": celsius, "fahrenheit": celsius * 9/5 + 32}
#     
#     def write_data(self, **kwargs):
#         pass  # Read-only sensor
#     
#     def handle_osc_message(self, path, args):
#         if path == f"/{self.name}/read":
#             data = self.read_data()
#             return (f"/{self.name}/data", [data['celsius']])
#         return None
#     
#     def cleanup(self):
#         pass