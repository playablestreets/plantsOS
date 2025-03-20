#!/usr/bin/env python3
"""
Headless USB Keyboard Listener for Raspberry Pi
This script captures keystrokes from an attached USB keyboard
even when running in headless mode (no display).
"""

import evdev
from evdev import categorize, ecodes
import time
import os
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='keyboard_listener.log'
)

def find_keyboard():
    """Find the first keyboard device connected to the system."""
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        # Look for devices that likely represent keyboards
        if 'keyboard' in device.name.lower() or any(
            keyboard_hint in device.phys.lower() 
            for keyboard_hint in ['kbd', 'keyboard', 'input0']
        ):
            logging.info(f"Found keyboard: {device.name}, {device.path}")
            return device
    
    logging.error("No keyboard found")
    return None

def process_key_event(event):
    """Process a key event and perform actions based on the key pressed."""
    if event.type == ecodes.EV_KEY:
        key_event = categorize(event)
        # Only process key press events (not releases or repeats)
        if key_event.keystate == key_event.key_down:
            key_name = key_event.keycode
            if isinstance(key_name, list):
                key_name = key_name[0]
                
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.info(f"Key pressed: {key_name}")
            
            # Example: Perform different actions based on keys pressed
            # You can customize these actions as needed
            if key_name == 'KEY_ESC':
                logging.info("ESC key pressed - exiting program")
                return False  # Signal to exit the program
            elif key_name == 'KEY_SPACE':
                logging.info("SPACE key pressed - special action")
                # Add your custom action here
            elif key_name.startswith('KEY_F'):
                function_key = key_name.replace('KEY_F', '')
                logging.info(f"Function key F{function_key} pressed")
                # Add function key specific actions here
                
            # Save all keystrokes to a file
            with open('keystroke_log.txt', 'a') as f:
                f.write(f"{timestamp}: {key_name}\n")
                
    return True  # Continue listening

def main():
    """Main function to run the keyboard listener."""
    try:
        # Find the keyboard device
        keyboard = find_keyboard()
        if not keyboard:
            print("No keyboard found. Exiting.")
            return
        
        print(f"Listening for keystrokes from: {keyboard.name}")
        print("Press ESC key to exit")
        
        # Register the keyboard device for exclusive access
        # This prevents keystroke events from being sent to other applications
        keyboard.grab()
        
        # Create a log file if it doesn't exist
        if not os.path.exists('keystroke_log.txt'):
            with open('keystroke_log.txt', 'w') as f:
                f.write(f"Keystroke Log - Started {datetime.now()}\n")
        
        # Main event loop
        for event in keyboard.read_loop():
            if not process_key_event(event):
                break
                
    except Exception as e:
        logging.error(f"Error: {e}")
        print(f"Error: {e}")
    finally:
        # Always release the keyboard if we've grabbed it
        if 'keyboard' in locals() and keyboard:
            keyboard.ungrab()
            print("Keyboard released. Program terminated.")

if __name__ == "__main__":
    main()