import os, sys
from time import sleep
from csv import reader
from pyOSC3 import OSCServer, OSCClient, OSCMessage
import atexit

server = OSCServer( ('', 7770) )
client = OSCClient()
client.connect( ('127.0.0.1', 6661) )


def config_callback(path='', tags='', args='', source=''):
    # NOTE: On Raspbian Trixie (Debian 13+), hostname changes must be made using hostnamectl.
    # Direct edits to /etc/hostname are discouraged and may not update mDNS/Bonjour (.local) names.
    # avahi-daemon provides .local (Bonjour/mDNS) resolution and listens for hostname changes via systemd.
    # After changing the hostname, avahi-daemon is restarted to ensure the .local address updates immediately.
    # /etc/hosts is also updated for local resolution of the new hostname.

    directory = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(directory, "../bopos.devices")
    print("loading: ", config_file)

    # open file in read mode
    with open(config_file, 'r') as read_obj:
        csv_reader = reader(read_obj, skipinitialspace=True)
        macfound = False
        for row in csv_reader:
            # row variable is a list that represents a row in csv
            # sys.argv[1] is mac address passed in at run
            # row[0] is mac address in config file
            # row[1] is hostname in config file
            # row[2] is ID in config file
            if row[0] == sys.argv[1]:
                print('MAC address found in bopos.devices')
                macfound = True
                hostname = row[1]
                print('setting hostname to ' + hostname)

                # Use hostnamectl for systemd-based systems (Debian 13/Trixie)
                os.system(f'sudo hostnamectl set-hostname {hostname}')
                # Update /etc/hosts for local resolution
                os.system(f"sudo sed -i 's/^127.0.1.1.*/127.0.1.1   {hostname}/' /etc/hosts")

                # Ensure avahi-daemon is running and restart it to update mDNS (.local)
                avahi_status = os.system('systemctl is-active --quiet avahi-daemon')
                if avahi_status == 0:
                    print('Restarting avahi-daemon to update mDNS hostname...')
                    os.system('sudo systemctl restart avahi-daemon')
                else:
                    print('avahi-daemon is not active. Attempting to start...')
                    os.system('sudo systemctl start avahi-daemon')

                id = row[2]
                print('setting ID to ' + id)
                msg = OSCMessage("/id")
                msg.append(id, 'f')
                client.send(msg)
                break
        if not macfound:
            print('MAC address not found in bopos.devices.csv')


def update_callback(path='', tags='', args='', source=''):
    directory = os.path.dirname(os.path.realpath(__file__))
    update_script = os.path.join(directory, "../bash/update.sh")
    msg = OSCMessage("/update")
    client.send(msg)
    print("UPDATE!")
    os.system(update_script)

def getsamples_callback(path='', tags='', args='', source=''):
    directory = os.path.dirname(os.path.realpath(__file__))
    update_script = os.path.join(directory, "../bash/getsamples.sh")
    msg = OSCMessage("/getsamples")
    client.send(msg)
    print("UPDATE SAMPLES!")
    os.system(update_script)        

def shutdown_callback(path='', tags='', args='', source=''):
    msg = OSCMessage("/shutdown")
    client.send(msg)    
    print("SHUTDOWN!")
    os.system("systemctl poweroff")

def reboot_callback(path='', tags='', args='', source=''):
    msg = OSCMessage("/reboot")
    client.send(msg)    
    print("REBOOTING")
    os.system("systemctl reboot")

def checkout_callback(path, tags, args, source):
    msg = OSCMessage("/checkout")
    client.send(msg)    
    branch = args[0].lstrip('/')
    directory = os.path.dirname(os.path.realpath(__file__))
    print("checking out: " + branch)
    checkout_script = os.path.join(directory, "../bash/checkout.sh ") + branch
    os.system(checkout_script)

    # directory = os.path.dirname(os.path.realpath(__file__))
    update_script = os.path.join(directory, "../bash/update.sh")
    msg = OSCMessage("/update")
    client.send(msg)
    print("UPDATE!")
    os.system(update_script)

def exit_handler():
    print("exiting.  closing server...")
    server.close()


server.addMsgHandler( "/config", config_callback )
server.addMsgHandler( "/update", update_callback )
server.addMsgHandler( "/getsamples", getsamples_callback )
server.addMsgHandler( "/shutdown", shutdown_callback )
server.addMsgHandler( "/reboot", reboot_callback )
server.addMsgHandler( "/checkout", checkout_callback )
atexit.register(exit_handler)

#ARG 1 MAC Address
if __name__ == "__main__":

    # config_callback()

    while True:
        sleep(1)
        server.handle_request()
