from time import sleep
from pyOSC3 import OSCClient, OSCMessage
from PiicoDev_LIS3DH import PiicoDev_LIS3DH
from PiicoDev_Unified import sleep_ms # cross-platform compatible sleep function
# from piicodev.board import PiicoDev
import atexit
import socket

motion = PiicoDev_LIS3DH()

# Set up the OSC client
client = OSCClient()
client.connect(("localhost", 1110)) # Connect to the OSC receiver


while True:
	try:
		print("Sending LIS3DH data to localhost:1110. Press Ctrl+C to stop.")
		while True:
			# Read acceleration data
			# x = accel.acceleration("x")
			# y = accel.acceleration("y")
			# z = accel.acceleration("z")
			x, y, z = motion.angle # Tilt could be measured with respect to three different axes
			
			msg_tilt = OSCMessage("/tilt");
			msg_tilt.append(x,'f')
			msg_tilt.append(y,'f')
			msg_tilt.append(z,'f')

			client.sent(msg_tilt)

			# Create OSC messages
			# msg_x = OSCMessage("/accel/x", x)
			# msg_y = OSCMessage("/accel/y", y)
			# msg_z = OSCMessage("/accel/z", z)

			# Send the messages
			# client.send(msg_x)
			# client.send(msg_y)
			# client.send(msg_z)

			# print("Angle: {:.0f}°".format(y)) # Print the angle of rotation around the y-axis
			

			# Print data
			print(f"X: {x: .2f}, Y: {y: .2f}, Z: {z: .2f}")
			
			sleep(0.1) # Wait 100 milliseconds



	except KeyboardInterrupt:
		print("Script terminated by user.")
		
	except Exception as e:
		print(f"An error occurred: {e}")



