# plantsOS Testing

## Requirements 

- puredata 0.54+ vanilla 
- pd-comport (install via Deken)


## Installation

```
#Clone repo and include submodules:
https://github.com/playablestreets/plantsOS.git --recursive

# Checkout testing branch
cd plantsOS
git checkout testing
```

Open 

## OSC schema

ESP32 outputs SLIP encoded OSC over serial to PD as per schema:


### Touch Sensors
Output normalised values from 0.0 to 1.0, 1 = touched and 0 = floor
Output raw values from MPR

```
/t/[sensorIndex]/[touchIndex] (float)0.0 - 1.0
/traw/[sensorIndex]/[touchIndex] (int)0 - 4096
```

### Buttons
```
/b/[buttonIndex] (int)0 - 1
```

### Pots
```
/p/[potIndex] (float)0.0 - 1.0

```
