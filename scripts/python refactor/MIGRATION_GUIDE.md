# Migration Guide: Old → New Architecture

## Key Changes

### 1. **Simplified Main Loop**
**Before:** Complex threading, individual OSC handlers, mixed polling/response logic
**After:** Simple `while` loop that polls and sends one OSC bundle

### 2. **Dynamic Peripheral Creation**
**Before:** Peripherals hardcoded in `setup_peripherals()`
**After:** Create via OSC: `[io/create adc1 ads1015 0x48(`

### 3. **Single OSC Bundle**
**Before:** Each peripheral sent individual OSC messages
**After:** One bundle containing all peripheral data

### 4. **Simplified Peripheral Interface**
**Before:** Complex `handle_osc_message()`, `poll()`, individual OSC paths
**After:** Just `read_data()` and `write_data()`

## Code Comparison

### Main Loop

**Before (OLD):**
```python
def poll_loop():
    while polling:
        for device in peripherals:
            response = device.poll()
            if response:
                osc_path, osc_args = response
                # Send individual message
                osc_client.sendto(msg, pd_address)
        time.sleep(1.0 / POLL_RATE)

def handle_osc(path, tags, args, source):
    for device in peripherals:
        response = device.handle_osc_message(path, args)
        if response:
            # Send response
            ...
```

**After (NEW):**
```python
def poll_and_send(self):
    bundle = osc_bundle_builder.OscBundleBuilder()
    
    for name, peripheral in self.peripherals.items():
        data = peripheral.read_data()
        msg = osc_message_builder.OscMessageBuilder(f"/{name}/data")
        # Add data to message
        bundle.add_content(msg.build())
    
    self.osc_client.send(bundle.build())

while running:
    poll_and_send()
    time.sleep(1.0 / poll_rate)
```

### Peripheral Implementation

**Before (OLD - ADC):**
```python
class ADC:
    def read_data(self):
        values = [self.ch0.voltage, ...]
        return ("/adc/data", values)
    
    def poll(self):
        return self.read_data()
    
    def handle_osc_message(self, path, args):
        if path == "/adc/read":
            return self.read_data()
        elif path == "/adc/ch0":
            return ("/adc/ch0", [self.ch0.voltage])
        # ... many more paths
```

**After (NEW - ADC):**
```python
class ADC:
    def read_data(self):
        return [self.ch0.voltage, self.ch1.voltage, ...]
    
    def write_data(self, **kwargs):
        pass  # Read-only
```

## Migration Steps

### 1. Update main.py
Replace your old `main.py` with `main_new.py`

### 2. Update peripherals
Replace peripheral files:
- `peripheral_adc.py` → `peripheral_adc_new.py`
- `peripheral_tilt.py` → `peripheral_tilt_new.py`
- `peripheral_touch.py` → `peripheral_touch_new.py`

### 3. Update Pure Data patch

**OLD way - separate receive objects:**
```
[netreceive 8880]
|
[route /adc/data /tilt/data /touch/data]
```

**NEW way - receive bundle:**
```
[oscreceive 6662]
|
[oscformat]
|
[route /adc1/data /tilt/data /touch/data]
```

**Create peripherals at startup:**
```
[loadbang]
|
[io/create adc1 ads1015 0x48(
|
[io/create tilt lis3dh 0x19(
|
[oscsend 127.0.0.1 8880]
```

## Feature Comparison

| Feature | Old | New |
|---------|-----|-----|
| Peripheral creation | Hardcoded | Dynamic via OSC |
| Data format | Individual messages | Single bundle |
| Poll control | Fixed in code | OSC command |
| OSC library | pyOSC3 | python-osc |
| Line count | ~400 | ~200 |
| Peripheral methods | 5-6 | 3 |

## Benefits of New Architecture

✅ **50% less code** - Simpler to understand and maintain
✅ **Dynamic creation** - No code changes to add peripherals
✅ **Atomic updates** - All sensor data arrives together
✅ **Better sync** - One bundle = one timestamp
✅ **Easier debugging** - Single bundle to inspect
✅ **More flexible** - Change poll rate without restart

## Breaking Changes

⚠️ **OSC paths changed:**
- Old: `/adc/data`, `/tilt/data`
- New: `/adc1/data`, `/tilt/data` (custom names)

⚠️ **No individual channel requests:**
- Old: Could request `/adc/ch0` separately
- New: All channels sent together (filter in PD)

⚠️ **Different OSC library:**
- Old: `pyOSC3`
- New: `python-osc`

## Backwards Compatibility

If you need the old behavior:
- Keep individual OSC handlers in peripherals
- Parse `command` in `write_data()` to handle custom paths
- Example in `peripheral_touch_new.py` (threshold command)
