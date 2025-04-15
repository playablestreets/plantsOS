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


## OSC schema

ESP32 outputs SLIP encoded OSC over serial to PD as per schema:


### Touch Sensors
- Output an array of values normalised between 0.0 and 1.0; 1 = touched and 0 = floor

```
/t i f ...
/t [sensorIndex] [t0 ... tn]
```
*Example: /t 1 0 0.5*

- Output an array of raw values from MPR
```
  // /traw i i ...
  // /traw [sensorIndex] [t0 ... tn]
```
*Example: /traw 0 1 1500*

### Buttons
```
/b ii
/b [buttonIndex] (int)0 - 1
```
*Example: /b 2 1*

### Pots
```
/b if
/p [potIndex] (float)0.0 - 1.0
```
*Example: /p 1 0.5*
