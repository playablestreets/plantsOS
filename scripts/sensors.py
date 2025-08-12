from time import sleep
from pyOSC3 import OSCClient, OSCMessage
from PiicoDev_LIS3DH import PiicoDev_LIS3DH
from PiicoDev_Unified import sleep_ms # cross-platform compatible sleep function

motion = PiicoDev_LIS3DH()

# Set up the OSC client
client = OSCClient()
client.connect( ('127.0.0.1', 8880) ) # Connect to the OSC receiver


while True:

	print("Sending LIS3DH data to localhost:8880. Press Ctrl+C to stop.")
	x, y, z = motion.angle # Tilt could be measured with respect to three different axes
	
	msg_tilt = OSCMessage("/tilt");
	msg_tilt.append(x,'f')
	msg_tilt.append(y,'f')
	msg_tilt.append(z,'f')

	client.send(msg_tilt)


	# Print data
	print(f"X: {x: .2f}, Y: {y: .2f}, Z: {z: .2f}")
	
	sleep(0.2) # Wait 200 milliseconds

