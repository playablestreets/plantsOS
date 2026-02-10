from time import sleep
from pyOSC3 import OSCClient, OSCMessage
from PiicoDev_LIS3DH import PiicoDev_LIS3DH
from PiicoDev_CAP1203 import PiicoDev_CAP1203
from PiicoDev_Unified import sleep_ms

# Initialize the two PiicoDev boards
motion = PiicoDev_LIS3DH()
# touch_sensor = PiicoDev_CAP1203(touchmode='single', sensitivity=6)
touch_sensor = PiicoDev_CAP1203(sensitivity=1)

# Set up the OSC client
client = OSCClient()
client.connect( ('127.0.0.1', 8880) )

print("Sending LIS3DH and CAP1203 data to localhost:8880. Press Ctrl+C to stop.")

# Initialize previous values to None
prev_x, prev_y, prev_z = None, None, None
prev_status = [None, None, None]

while True:
    # Get data from the LIS3DH Gyro
    x, y, z = motion.angle
    
    # Check if any tilt value has changed
    if x != prev_x or y != prev_y or z != prev_z:
        msg_tilt = OSCMessage("/tilt")
        msg_tilt.append(x, 'f')
        msg_tilt.append(y, 'f')
        msg_tilt.append(z, 'f')
        client.send(msg_tilt)
        
        # Update previous values
        prev_x, prev_y, prev_z = x, y, z

    # Get data from the CAP1203 Touch Sensor
    status = touch_sensor.read()
    
    # Check if any touch status has changed
    if status[1] != prev_status[0] or status[2] != prev_status[1] or status[3] != prev_status[2]:
        msg_touch = OSCMessage("/touch")
        msg_touch.append(float(status[1]), 'f')
        msg_touch.append(float(status[2]), 'f')
        msg_touch.append(float(status[3]), 'f')
        client.send(msg_touch)

        # Update previous values
        prev_status = [status[1], status[2], status[3]]
    
    sleep(0.02)