# plantsOS Testing

## Requirements 

- puredata 0.54+ vanilla 
- pd-comport (install via Deken)


## Installation


Clone repo and include submodules:
```
https://github.com/playablestreets/plantsOS.git --recursive
```

Checkout testing branch
```
cd plantsOS
git checkout testing
```

In PD confirm comport external is installed via deken:
help -> find externals -> (search \'comport\')


# OSC schema

## To PD
ESP32 outputs SLIP encoded OSC over serial to PD as per schema:


### Touch Sensors
- Output an array of values normalised between 0.0 and 1.0; 1 = touched and 0 = floor

```
/t i f ...
/t [MPRIndex] [t0 ... tn]
```
*Example: /t 1 0 0.5*

- Output an array of raw values from MPR
```
  // /traw i i ...
  // /traw [MPRIndex] [t0 ... tn]
```
*Example: /traw 0 1 1500*

### Buttons
```
/b ii
/b [buttonIndex] (int)0-1
```
*Example: /b 2 1*

### Pots
```
/b if
/p [potIndex] (float)0.0-1.0
```
*Example: /p 1 0.5*



## To ESP32
From PD to ESP via comport, slip encoded OSC as per schema:

### First Filter Iteration
```
/ffi ii
/ffi [MPRIndex] (int)0-3
```
*Example: /ffi 0 3*

### Charge Discharge Current
```
/cdc ii
/cdc [MPRIndex] (int)1-63
```
*Example: /cdc 1 18*

### Charge Discharge Time
```
/cdt ii
/cdt [MPRIndex] (int)1-7
```
*Example: /cdt 0 4*

### Second Filter Iteration
```
/sfi ii
/sfi [MPRIndex] (int)0-3
```
*Example: /sfi 0 0*

### Electrode Sample Interval
```
/esi ii
/esi [MPRIndex] (int)0-7
```
*Example: /esi 0 2*
