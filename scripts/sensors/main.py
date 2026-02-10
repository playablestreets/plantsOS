from time import sleep
import threading
from pyOSC3 import OSCServer, OSCClient, OSCMessage, OSCClientError
import board
import busio
import adafruit_mpr121
# import smbus2
from peripheral_adc import ADC

# Settings
I2C_BUS = 1  # Not used by Adafruit library, but kept for consistency
PYTHON_LISTEN_PORT = 8881  # Python listens here for PD commands
PD_LISTEN_PORT = 8880      # Pure Data listens here for data from Python


# List of all your peripherals
peripherals = []

def setup_peripherals():
    """Create and initialize all devices"""
    global peripherals

    # bus = smbus2.SMBus(I2C_BUS)  

    adc = ADC(bus=None, address=0x48)  # Address for ADS1015
    adc.setup()
    peripherals.append(adc)

    # Add whichever devices you're using
    # accel = Accelerometer(bus, address=0x68)
    # accel.setup()
    # peripherals.append(accel)
    
    # temp = TemperatureSensor(bus, address=0x48)
    # temp.setup()
    # peripherals.append(temp)
    
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
    """Print sensor values every second - comment out to disable"""
    while True:
        for device in peripherals:
            data = device.read_data()
            print(f"{device.name}: {data}")
        time.sleep(1)


def main():
    global server, osc_client
    
    # Setup OSC client (for sending TO Pure Data)
    osc_client = OSCClient()
    
    # Setup I2C devices
    setup_peripherals()
    
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


# # Set up the OSC client
# client = OSCClient()
# client.connect( ('127.0.0.1', OSC_PORT) )

# # I2C bus
# i2c = busio.I2C(board.SCL, board.SDA)

# # # ADS1015 ADC
# # adc = ADS1015.ADS1015(i2c)

# # channels = [
# #     AnalogIn(adc, ADS.Pin.A0),
# #     AnalogIn(adc, ADS.Pin.A1),
# #     AnalogIn(adc, ADS.Pin.A2),
# #     AnalogIn(adc, ADS.Pin.A3),
# # ]

# # MPR121 (default address 0x5A)
# mpr1 = adafruit_mpr121.MPR121(i2c, address=0x5A) 
# mpr2 = adafruit_mpr121.MPR121(i2c, address=0x5C)

# while True:
#     # Read ADC channels
#     for i, ch in enumerate(channels):
#         print(f"A{i}: raw={ch.value:6d}  voltage={ch.voltage:0.4f} V")



#     # msg_touch = OSCMessage("/touch")

#     # # Read MPR1 electrode 0
#     # touched = mpr1.filtered_data(0)
#     # print(f"MPR 1 E0: {touched:0.4f}")
#     # msg_touch.append(float(touched), 'f')

#     # # Read MPR1 electrode 0
#     # touched = mpr2.filtered_data(0)
#     # print(f"MPR 2 E0: {touched:0.4f}")
#     # msg_touch.append(float(touched), 'f')


#     # try:
#     #     client.send(msg_touch)
#     # except OSCClientError as e:
#     #     print(f"OSC client error: {e}")

#     print("-" * 40)
#     sleep(1)
