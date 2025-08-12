from time import sleep
from pyOSC3 import OSCClient, OSCMessage
from piicodev.lis3dh import PiicodevLIS3DH
from piicodev.board import PiicoDev
import atexit

# Set up the PiicoDev modules
accel = PiicodevLIS3DH()

# Define a cleanup function
def cleanup():
    """Closes all I2C connections when the script exits."""
    PiicoDev.close_all_i2c()
    print("I2C connections closed.")

# Register the cleanup function to be called on exit
atexit.register(cleanup)

# Set up the OSC client
client = OSCClient()
# client.connect(("localhost", 1110)) # Connect to the OSC receiver
client.connect(("255.255.255.255", 1110)) # Connect to the OSC receiver


# Main loop to read data and send it
try:
    # print("Sending LIS3DH data to localhost:1110. Press Ctrl+C to stop.")
    print("Broadcasting LIS3DH data to all devices on port 1110. Press Ctrl+C to stop.")
    while True:
        # Read acceleration data
        x = accel.acceleration("x")
        y = accel.acceleration("y")
        z = accel.acceleration("z")

        # Create OSC messages
        msg_x = OSCMessage("/accel/x", x)
        msg_y = OSCMessage("/accel/y", y)
        msg_z = OSCMessage("/accel/z", z)

        # Send the messages
        client.send(msg_x)
        client.send(msg_y)
        client.send(msg_z)

        # Print data
        print(f"X: {x: .2f}, Y: {y: .2f}, Z: {z: .2f}")
        
        sleep(0.1) # Wait 100 milliseconds

except KeyboardInterrupt:
    print("Script terminated by user.")
    
except Exception as e:
    print(f"An error occurred: {e}")