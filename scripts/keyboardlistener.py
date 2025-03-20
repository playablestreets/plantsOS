#!/usr/bin/env python3
"""
Simple Headless USB Keyboard to OSC Forwarder for Raspberry Pi
This script captures keystrokes from an attached USB keyboard
and forwards them as OSC messages to localhost:6662 using pyOSC3
"""

import evdev
from evdev import categorize, ecodes
import time
import sys
import os

from pyOSC3 import OSCServer, OSCClient, OSCMessage

# OSC client configuration
OSC_IP = "127.0.0.1"  # localhost
OSC_PORT = 6662

def find_keyboard():
    """Find the first keyboard device connected to the system."""
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        # Look for devices that likely represent keyboards
        if 'keyboard' in device.name.lower() or any(
            keyboard_hint in device.phys.lower() 
            for keyboard_hint in ['kbd', 'keyboard', 'input0']
        ):
            print(f"Found keyboard: {device.name}, {device.path}")
            return device
    
    print("No keyboard found")
    return None

def process_key_event(event, osc_client):
    """Process a key event and send it as an OSC message."""
    if event.type == ecodes.EV_KEY:
        key_event = categorize(event)
        # Get key state (0 = release, 1 = press, 2 = hold)
        key_state = key_event.keystate
        
        # Get key name
        key_name = key_event.keycode
        if isinstance(key_name, list):
            key_name = key_name[0]
        
        # Send the key event as an OSC message
        # Create OSC message
        msg = OSC3.OSCMessage()
        msg.setAddress("/keyboard/key")
        msg.append(key_name)
        msg.append(key_state)
        
        # Send the message
        osc_client.send(msg)
        
        # Send key-specific message
        key_msg = OSC3.OSCMessage()
        key_msg.setAddress(f"/keyboard/{key_name}")
        key_msg.append(key_state)
        osc_client.send(key_msg)
        
        # For debugging - print to console
        state_name = "pressed" if key_state == key_event.key_down else "released" if key_state == key_event.key_up else "held"
        print(f"Key {state_name}: {key_name}")
        
        # ESC key to exit the program
        if key_name == 'KEY_ESC' and key_state == key_event.key_down:
            print("ESC key pressed - exiting program")
            return False  # Signal to exit
            
    return True  # Continue listening

def main():
    """Main function to run the keyboard listener with OSC forwarding."""
    try:
        # Initialize OSC client using pyOSC3
        osc_client = OSC3.OSCClient()
        osc_client.connect((OSC_IP, OSC_PORT))
        print(f"OSC client initialized, forwarding to {OSC_IP}:{OSC_PORT}")
        
        # Find the keyboard device
        keyboard = find_keyboard()
        if not keyboard:
            print("No keyboard found. Exiting.")
            return
        
        print(f"Listening for keystrokes from: {keyboard.name}")
        print(f"Forwarding keystrokes as OSC messages to {OSC_IP}:{OSC_PORT}")
        print("Press ESC key to exit")
        
        # Send an initialization message
        init_msg = OSC3.OSCMessage()
        init_msg.setAddress("/keyboard/status")
        init_msg.append("connected")
        osc_client.send(init_msg)
        
        # Register the keyboard device for exclusive access
        keyboard.grab()
        
        # Main event loop
        for event in keyboard.read_loop():
            if not process_key_event(event, osc_client):
                break
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Always release the keyboard if we've grabbed it
        if 'keyboard' in locals() and keyboard:
            keyboard.ungrab()
            
            # Send a disconnection message if OSC client exists
            if 'osc_client' in locals() and osc_client:
                try:
                    disc_msg = OSC3.OSCMessage()
                    disc_msg.setAddress("/keyboard/status")
                    disc_msg.append("disconnected")
                    osc_client.send(disc_msg)
                except:
                    pass
                    
            print("Keyboard released. Program terminated.")

if __name__ == "__main__":
    main()