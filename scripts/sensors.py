from time import sleep
from pyOSC3 import OSCClient, OSCMessage
from PiicoDev_LIS3DH import PiicoDev_LIS3DH
from PiicoDev_CAP1203 import PiicoDev_CAP1203 # Import the CAP1203 library
from PiicoDev_Unified import sleep_ms # cross-platform compatible sleep function

# Initialize the two PiicoDev boards
motion = PiicoDev_LIS3DH()
touch_sensor = PiicoDev_CAP1203()

# Set up the OSC client
client = OSCClient()
client.connect( ('127.0.0.1', 8880) ) # Connect to the OSC receiver


while True:

    print("Sending LIS3DH and CAP1203 data to localhost:8880. Press Ctrl+C to stop.")

    # Get data from the LIS3DH Gyro
    x, y, z = motion.angle # Tilt could be measured with respect to three different axes
    
    msg_tilt = OSCMessage("/tilt");
    msg_tilt.append(x,'f')
    msg_tilt.append(y,'f')
    msg_tilt.append(z,'f')

    client.send(msg_tilt)

    # Get data from the CAP1203 Touch Sensor
    status = touch_sensor.read() # Read the touch status of the three pads (returns a list of booleans)

    msg_touch = OSCMessage("/touch");
    msg_touch.append(status[0], 'f') # Pad 1
    msg_touch.append(status[1], 'f') # Pad 2
    msg_touch.append(status[2], 'f') # Pad 3

    client.send(msg_touch)

    # Print data
    # print(f"X: {x: .2f}, Y: {y: .2f}, Z: {z: .2f} | Touch: {status}")
    
    sleep(0.1) # Wait 100 milliseconds
