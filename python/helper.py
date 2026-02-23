import shutil
import subprocess
import re


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

def switch_patch_callback(path='', tags='', args='', source=''):
    directory = os.path.dirname(os.path.realpath(__file__))
    patches_dir = os.path.join(directory, '../patches')
    active_patch_file = os.path.join(patches_dir, 'active_patch.txt')
    stop_script = os.path.join(directory, '../bash/stop.sh')
    start_script = os.path.join(directory, '../bash/start.sh')

    print ("Switching patch...")
    print(f"Received args: {args}")
    print(f"Patches directory: {patches_dir}")
    print(f"Active patch file: {active_patch_file}")
    print(f"Stop script: {stop_script}")
    print(f"Start script: {start_script}")
    print(f"Contents of patches directory: {os.listdir(patches_dir)}")
    print(f"Current active patch: {open(active_patch_file).read().strip() if os.path.exists(active_patch_file) else 'None'}")
    print(f"Running as user: {os.getlogin()}")

    if not args or not args[0]:
        print("No patch name provided to /switch_patch")
        return
    patch_name = args[0].strip()
    patch_path = os.path.join(patches_dir, patch_name)
    if not os.path.isdir(patch_path):
        print(f"Patch '{patch_name}' does not exist in patches directory.")
        return
    try:
        # Write new patch name to active_patch.txt
        with open(active_patch_file, 'w') as f:
            f.write(patch_name + '\n')
        print(f"Set active patch to: {patch_name}")
    except Exception as e:
        print(f"Failed to write active_patch.txt: {e}")
        return
    try:
        print("Running stop.sh with sudo...")
        stop_result = os.system(f"sudo {stop_script}")
        if stop_result != 0:
            print(f"stop.sh exited with code {stop_result}")
        else:
            print("stop.sh completed successfully.")
    except Exception as e:
        print(f"Failed to run stop.sh: {e}")
        return
    try:
        print("Running start.sh as user...")
        start_result = os.system(f"{start_script}")
        if start_result != 0:
            print(f"start.sh exited with code {start_result}")
        else:
            print("start.sh completed successfully.")
    except Exception as e:
        print(f"Failed to run start.sh: {e}")
        return
    # Optionally, send OSC confirmation
    try:
        msg = OSCMessage("/switch_patch")
        msg.append(patch_name)
        client.send(msg)
    except Exception as e:
        print(f"Failed to send OSC confirmation: {e}")




def add_patch_callback(path='', tags='', args='', source=''):
    directory = os.path.dirname(os.path.realpath(__file__))
    patches_dir = os.path.join(directory, '../patches')
    if not args or not args[0]:
        print("No repo provided to /addpatch")
        return
    repo_arg = args[0].strip()
    # Only allow user/repo format
    m = re.match(r'^([\w-]+)/([\w.-]+)$', repo_arg)
    if not m:
        print(f"Invalid repo format: {repo_arg}. Use user/repo.")
        return
    user, repo = m.groups()
    repo_url = f"https://github.com/{user}/{repo}.git"
    dest_dir = os.path.join(patches_dir, repo)
    # Check if repo exists on GitHub
    try:
        result = subprocess.run(["git", "ls-remote", repo_url], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        if result.returncode != 0:
            print(f"GitHub repo not found or not accessible: {repo_url}")
            return
    except Exception as e:
        print(f"Error checking repo: {e}")
        return
    # Remove existing folder if it exists
    if os.path.isdir(dest_dir):
        try:
            print(f"Removing existing patch folder: {dest_dir}")
            shutil.rmtree(dest_dir)
        except Exception as e:
            print(f"Failed to remove existing patch folder: {e}")
            return
    # Clone repo recursively
    try:
        print(f"Cloning {repo_url} into {dest_dir} (recursive)...")
        result = subprocess.run(["git", "clone", "--recursive", repo_url, dest_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print(f"Failed to clone repo: {result.stderr.decode().strip()}")
            return
        print(f"Successfully cloned {repo_url} into {dest_dir}")
    except Exception as e:
        print(f"Error cloning repo: {e}")
        return
    # Pull recursively (in case)
    try:
        print(f"Pulling submodules in {dest_dir}...")
        result = subprocess.run(["git", "pull", "--recurse-submodules"], cwd=dest_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print(f"Failed to pull submodules: {result.stderr.decode().strip()}")
        else:
            print("Submodules updated.")
    except Exception as e:
        print(f"Error pulling submodules: {e}")
    # Optionally, send OSC confirmation
    try:
        msg = OSCMessage("/addpatch")
        msg.append(repo_arg)
        client.send(msg)
    except Exception as e:
        print(f"Failed to send OSC confirmation: {e}")


def exit_handler():
    print("exiting.  closing server...")
    server.close()


server.addMsgHandler( "/config", config_callback )
server.addMsgHandler( "/update", update_callback )
server.addMsgHandler( "/getsamples", getsamples_callback )
server.addMsgHandler( "/shutdown", shutdown_callback )
server.addMsgHandler( "/reboot", reboot_callback )
server.addMsgHandler( "/checkout", checkout_callback )
server.addMsgHandler( "/patch", switch_patch_callback )
server.addMsgHandler( "/addpatch", add_patch_callback )
atexit.register(exit_handler)

#ARG 1 MAC Address
if __name__ == "__main__":

    # config_callback()

    while True:
        sleep(1)
        server.handle_request()
