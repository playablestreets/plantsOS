# Raspberry Pi I2C to Pure Data Bridge

A simple Python framework for connecting I2C peripherals on a Raspberry Pi to Pure Data via OSC.

## Project Structure
```
project/
├── main.py                  # Main entry point - start here
├── config.py               # Configuration (I2C bus, OSC port, etc.)
├── peripherals/            # Your I2C device modules
│   ├── template.py         # Template for creating new devices
│   ├── accelerometer.py    # Example: accelerometer
│   └── temperature.py      # Example: temperature sensor
└── README.md
```

## How It Works

1. **Each peripheral** is a Python class with standard methods
2. **OSC messages** are routed to the appropriate peripheral
3. **Pure Data** sends/receives data via OSC on port 8000 (configurable)


## Adding a New I2C Device

### Step 1: Create the peripheral file

1. Copy `peripherals/template.py` to `peripherals/yourdevice.py`
2. Rename the class from `PeripheralTemplate` to `YourDevice`
3. Change `self.name = "mydevice"` to something short like `"led"`

### Step 2: Fill in the methods

- **`setup()`** - Initialize your device (write config to I2C registers)
- **`read_data()`** - Read values from I2C, return as dict
- **`write_data()`** - Write values to I2C registers
- **`handle_osc_message()`** - Define OSC commands like `/led/on`

### Step 3: Add to main.py
```python
from peripherals.yourdevice import YourDevice

# In setup_peripherals():
yourdevice = YourDevice(bus, address=0x40)
yourdevice.setup()
peripherals.append(yourdevice)
```

## OSC Message Format

### From Pure Data to Python:
```
/devicename/command [arg1] [arg2] ...
```

Examples:
- `/accel/read` - no arguments
- `/led/brightness 128` - one argument
- `/rgb/color 255 128 0` - three arguments

### From Python to Pure Data:
Your device sends back:
```
/devicename/response [value1] [value2] ...
```

Examples:
- `/accel/data 0.5 -0.2 9.8` - x, y, z values
- `/temp/data 23.5` - temperature
- `/led/status ok` - status message

## Finding I2C Addresses

Use `i2cdetect` to find your device addresses:
```bash
i2cdetect -y 1
```

Common addresses:
- `0x68` - MPU6050 accelerometer
- `0x48` - TMP102 temperature sensor
- `0x76` - BMP280 pressure sensor

## Common I2C Operations

### Read a single byte:
```python
value = self.bus.read_byte_data(self.address, register)
```

### Write a single byte:
```python
self.bus.write_byte_data(self.address, register, value)
```

### Read multiple bytes:
```python
data = self.bus.read_i2c_block_data(self.address, register, num_bytes)
```

### Write multiple bytes:
```python
self.bus.write_i2c_block_data(self.address, register, [byte1, byte2, byte3])
```

## Troubleshooting

**"Remote I/O error"**
- Check your I2C address with `i2cdetect`
- Verify wiring (SDA, SCL, VCC, GND)
- Make sure I2C is enabled: `sudo raspi-config`

**OSC not receiving in Pure Data**
- Check the port matches (default 8000)
- Test with: `[udpreceive 8000]` in Pure Data
- Make sure firewall allows UDP

**Device not responding**
- Check if `setup()` was called
- Verify the device needs power-up time
- Some devices need multiple init steps

## Tips

- **Start simple**: Test I2C reads with a basic script first
- **Check datasheets**: Register addresses are device-specific
- **Use logging**: Add `print()` statements to debug
- **One device at a time**: Get one working before adding more
- **Test OSC separately**: Use Pure Data's `[sendOSC]` to test

## Support

- I2C basics: https://learn.sparkfun.com/tutorials/i2c
- Pure Data OSC: Search for "OSC Pure Data tutorial"
- Raspberry Pi I2C: https://www.raspberrypi.com/documentation/