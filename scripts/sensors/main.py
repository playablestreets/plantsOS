import sys
import os
import time
import threading

from pyOSC3 import OSCServer, OSCClient, OSCMessage, OSCClientError
import board
import busio
import adafruit_mpr121
# import smbus2
from peripheral_adc import ADC
from peripheral_tilt import Tilt

# Settings
I2C_BUS = 1  # Not used by Adafruit library, but kept for consistency
PYTHON_LISTEN_PORT = 8880  # Python listens here for PD commands
PD_LISTEN_PORT = 6662      # Pure Data listens here for data from Python


# List of all your peripherals
peripherals = []
osc_client = None
polling = False

def setup_peripherals():
    """Create and initialize all devices"""
    global peripherals

    # bus = smbus2.SMBus(I2C_BUS)  

    adc = ADC(bus=None, address=0x48)  # Address for ADS1015
    adc.setup()
    peripherals.append(adc)

    print(f"Initialized {len(peripherals)} devices")

def handle_osc(path, tags, args, source):
    """Route OSC messages to the right peripheral"""
    for device in peripherals:
        response = device.handle_osc_message(path, args)
        if response:
            print(f"Got response: {response}")
            # Send response back to Pure Data
            osc_path, osc_args = response
            # source[0] is the IP, source[1] is the port PD is listening on
            osc_client.sendto(osc_path, osc_args, (source[0], PD_LISTEN_PORT))
            break


def debug_print_sensors():
    """Print sensor values every second"""
    while True:
        for device in peripherals:
            data = device.read_data()
            print(f"{device.name}: {data}")
        sleep(1)


def main():
    global server, osc_client, polling
    
    # Setup OSC client (for sending TO Pure Data)
    osc_client = OSCClient()
    
    # Setup I2C devices
    setup_peripherals()

    # Start polling (comment out to disable)
    polling = True
    poll_thread = threading.Thread(target=poll_loop)
    poll_thread.daemon = True
    poll_thread.start()
    print(f"Polling at {POLL_RATE} Hz")    
    
    # Uncomment to see sensor values printed every second:
    threading.Thread(target=debug_print_sensors, daemon=True).start()

    # Setup OSC server (for receiving FROM Pure Data)
    server = OSCServer(('127.0.0.1', PYTHON_LISTEN_PORT))
    server.addMsgHandler("default", handle_osc)
    
    print(f"Python listening on port {PYTHON_LISTEN_PORT}")
    print(f"Sending to Pure Data on port {PD_LISTEN_PORT}")
    print("Press Ctrl+C to quit")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.close()

if __name__ == "__main__":
    main()

