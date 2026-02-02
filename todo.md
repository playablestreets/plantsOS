- Broadcast MAC, ip address, and hostname on boot
- set hostname on start from helper.py
-  Structure Python for multiple peripherals

## Simplified Structure

```
project/
├── main.py
├── peripherals/
│   ├── accelerometer.py
│   ├── temperature.py
│   └── display.py
└── config.py
```

## Simple Peripheral Template

Each peripheral is just a class with standard methods:

```python
# peripherals/accelerometer.py

class Accelerometer:
    def __init__(self, bus, address=0x68):
        self.bus = bus
        self.address = address
        self.name = "accel"  # Used for OSC paths
    
    def setup(self):
        """Initialize the hardware"""
        # Write to I2C registers to configure
        self.bus.write_byte_data(self.address, 0x6B, 0)
    
    def read_data(self):
        """Read current values"""
        # Read I2C data
        x = self.bus.read_byte_data(self.address, 0x3B)
        y = self.bus.read_byte_data(self.address, 0x3D)
        z = self.bus.read_byte_data(self.address, 0x3F)
        return {"x": x, "y": y, "z": z}
    
    def handle_osc_message(self, path, args):
        """Handle incoming OSC messages for this device"""
        if path == f"/{self.name}/read":
            data = self.read_data()
            # Return OSC message to send back
            return (f"/{self.name}/data", [data['x'], data['y'], data['z']])
        
        elif path == f"/{self.name}/calibrate":
            # Do calibration
            return (f"/{self.name}/status", ["calibrated"])
        
        return None
```

```python
# peripherals/temperature.py

class TemperatureSensor:
    def __init__(self, bus, address=0x48):
        self.bus = bus
        self.address = address
        self.name = "temp"
    
    def setup(self):
        """Initialize the hardware"""
        pass  # Some sensors don't need init
    
    def read_data(self):
        """Read temperature"""
        raw = self.bus.read_word_data(self.address, 0x00)
        temp = raw * 0.0625  # Convert to celsius
        return {"celsius": temp}
    
    def handle_osc_message(self, path, args):
        """Handle OSC for this device"""
        if path == f"/{self.name}/read":
            data = self.read_data()
            return (f"/{self.name}/data", [data['celsius']])
        
        return None
```

## Main Program

```python
# main.py
import smbus2
from OSC3 import OSCServer
from peripherals.accelerometer import Accelerometer
from peripherals.temperature import TemperatureSensor

# Settings
I2C_BUS = 1
OSC_PORT = 8000

# List of all your peripherals
peripherals = []

def setup_peripherals():
    """Create and initialize all devices"""
    global peripherals
    
    bus = smbus2.SMBus(I2C_BUS)
    
    # Add whichever devices you're using
    accel = Accelerometer(bus, address=0x68)
    accel.setup()
    peripherals.append(accel)
    
    temp = TemperatureSensor(bus, address=0x48)
    temp.setup()
    peripherals.append(temp)
    
    print(f"Initialized {len(peripherals)} devices")

def handle_osc(path, tags, args, source):
    """Route OSC messages to the right peripheral"""
    for device in peripherals:
        response = device.handle_osc_message(path, args)
        if response:
            # Send response back to Pure Data
            osc_path, osc_args = response
            server.sendOSC(osc_path, osc_args, source)
            break

def main():
    global server
    
    # Setup I2C devices
    setup_peripherals()
    
    # Setup OSC server
    server = OSCServer(('127.0.0.1', OSC_PORT))
    server.addMsgHandler("default", handle_osc)  # Catch all messages
    
    print(f"OSC server listening on port {OSC_PORT}")
    print("Press Ctrl+C to quit")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.close()

if __name__ == "__main__":
    main()
```

## How to Add a New Device

1. **Copy** an existing peripheral file
2. **Change** the class name and `self.name`
3. **Fill in** the `setup()` and `read_data()` methods with your I2C code
4. **Add** any OSC commands you need in `handle_osc_message()`
5. **Import** and add it in `main.py`

## Key Points

- **Each peripheral file is independent** - just implements 3 methods
- **OSC logic lives in each peripheral** - keeps related code together  
- **Main.py is the only place you edit** to add/remove devices
- **No abstract classes or inheritance** - just regular classes with the same method names
