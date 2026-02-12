# BopOS I2C to OSC Bridge

Simple Python bridge for interfacing I2C sensors with Pure Data via OSC.

## Architecture

**Super Simple Design:**
- Python polls all sensors at a defined rate (default 10 Hz)
- Sends a single OSC bundle containing data from all peripherals
- PD sends OSC commands to Python to control peripherals
- Peripherals can be created dynamically via OSC

## Quick Start

### 1. Run the Python script
```bash
python3 main.py
```

### 2. From Pure Data, create peripherals dynamically

```
[io/create adc1 ads1015 0x48(  ← Create ADC at address 0x48
[io/create tilt lis3dh 0x19(   ← Create tilt sensor
[io/create touch mpr121 0x5A(  ← Create touch sensor
```

### 3. Receive data bundle in PD

All sensor data arrives in a single OSC bundle at the poll rate:
```
/adc1/data 3.3 1.2 0.0 0.5
/tilt/data 0.1 -0.5 0.9
/touch/data 512 234 789 ... (12 values)
```

### 4. Control poll rate
```
[poll 20(  ← Poll at 20 Hz
[poll 5(   ← Poll at 5 Hz
```

### 5. Send commands to peripherals
```
[touch/threshold 15 8(  ← Set touch thresholds
```

## File Structure

```
main.py                    # Main OSC bridge (NEW - simplified!)
peripheral_adc.py          # ADS1015 ADC module
peripheral_tilt.py         # LIS3DH accelerometer
peripheral_touch.py        # MPR121 touch sensor
peripheral_template.py     # Template for new peripherals
```

## How It Works

### Main Loop (main.py)
```python
while running:
    poll_and_send()  # Read all peripherals, send OSC bundle
    sleep(1.0 / poll_rate)
```

### Peripheral Interface
Every peripheral has these simple methods:

```python
class MyPeripheral:
    def setup(self):
        # Initialize hardware
        
    def read_data(self):
        # Return list, dict, or value
        return [value1, value2, value3]
    
    def write_data(self, **kwargs):
        # Handle commands from PD
        command = kwargs.get('command')
        args = kwargs.get('args')
        
    def cleanup(self):
        # Shutdown cleanup
```

## OSC Commands

### System Commands
```
/io/create <name> <type> <address>   Create a peripheral
/io/list                             List active peripherals
/poll <rate>                         Set poll rate in Hz
```

### Peripheral Commands
```
/<peripheral>/<command> [args...]    Send command to peripheral
```

## Available Peripheral Types

| Type | Module | Class | Description |
|------|--------|-------|-------------|
| `ads1015` | peripheral_adc | ADC | 4-channel 12-bit ADC |
| `lis3dh` | peripheral_tilt | Tilt | 3-axis accelerometer |
| `mpr121` | peripheral_touch | Touch | 12-channel capacitive touch |

## Creating New Peripherals

1. Copy `peripheral_template.py` to `peripheral_yourdevice.py`
2. Fill in `setup()`, `read_data()`, and `write_data()`
3. Add to `PERIPHERAL_TYPES` in `main.py`:
```python
PERIPHERAL_TYPES = {
    'ads1015': ('peripheral_adc', 'ADC'),
    'yourdevice': ('peripheral_yourdevice', 'YourDevice'),
}
```
4. Create from PD: `[io/create dev1 yourdevice 0x48(`

## Examples

### Auto-create peripherals at startup
Edit `main.py`:
```python
def main():
    manager = IOManager()
    
    # Auto-create peripherals
    manager.create_peripheral('adc', 'ads1015', 0x48)
    manager.create_peripheral('tilt', 'lis3dh', 0x19)
    
    manager.run()
```

### Simple PD Patch
```
[metro 100]  ← Receive bundles automatically
|
[oscformat]  ← Unpack bundle
|
[route /adc1/data /tilt/data /touch/data]
|       |          |
[unpack f f f f]   [unpack f f f]   [unpack f f f f ...]
```

## Dependencies

```bash
pip3 install python-osc
pip3 install adafruit-circuitpython-ads1x15
pip3 install adafruit-circuitpython-mpr121
pip3 install piicodev-lis3dh
```

## Design Principles

✅ **Simple** - One polling loop, one OSC bundle
✅ **Readable** - Minimal code, clear structure  
✅ **Dynamic** - Create peripherals at runtime
✅ **Consistent** - All peripherals use same interface
✅ **Modular** - Easy to add new devices

## Troubleshooting

**No data in PD?**
- Check PD is listening on port 6662
- Check Python shows "Sending to PD on port 6662"
- Try `[io/list(` to see active peripherals

**Can't create peripheral?**
- Check I2C address with `i2cdetect -y 1`
- Check device type is in `PERIPHERAL_TYPES`
- Check peripheral module is in same directory

**Slow performance?**
- Lower poll rate: `[poll 5(`
- Reduce number of active peripherals
