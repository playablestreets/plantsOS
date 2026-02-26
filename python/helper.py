
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

    import socket
    current_hostname = socket.gethostname()
    reboot_required = False

    with open(config_file, 'r') as read_obj:
        csv_reader = reader(read_obj, skipinitialspace=True)
        macfound = False
        for row in csv_reader:
            if row[0] == sys.argv[1]:
                print('MAC address found in bopos.devices')
                macfound = True
                hostname = row[1]
                print('setting hostname to ' + hostname)


                if current_hostname != hostname:
                    reboot_required = True
                    msg = OSCMessage("/announce")
                    msg.append("Reboot required for hostname change.")
                    client.send(msg)
                    print(f"OSC announcement sent: Reboot required for hostname change. Current: {current_hostname}, Expected: {hostname}")

                    # Only change hostname if needed
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
    active_patch_file = os.path.realpath(os.path.join(patches_dir, 'active_patch.txt'))
    stop_script = os.path.realpath(os.path.join(directory, '../bash/stop.sh'))
    start_script = os.path.realpath(os.path.join(directory, '../bash/start.sh'))

    if not args or not args[0]:
        print("No patch name provided to /patch")
        return

    patch_name = args[0].strip()
    patch_path = os.path.join(patches_dir, patch_name)

    if not os.path.isdir(patch_path):
        print(f"Patch '{patch_name}' not found in {patches_dir}")
        return

    # Check that the patch has a main.pd entrypoint
    if not os.path.isfile(os.path.join(patch_path, 'main.pd')):
        print(f"Patch '{patch_name}' has no main.pd — cannot switch")
        return

    current = open(active_patch_file).read().strip() if os.path.exists(active_patch_file) else 'None'
    print(f"Switching patch: {current} -> {patch_name}")

    # Write new patch name
    try:
        with open(active_patch_file, 'w') as f:
            f.write(patch_name + '\n')
        print(f"Active patch set to: {patch_name}")
    except Exception as e:
        print(f"Failed to write active_patch.txt: {e}")
        return

    # Spawn a detached bash process to stop and restart.
    # This MUST be bash (not python) because stop.sh runs "pkill python"
    # which would kill this process. The bash process survives.
    restart_cmd = f"setsid bash -c '{stop_script}; sleep 2; {start_script}' > /dev/null 2>&1 &"
    print(f"Spawning restart: {restart_cmd}")
    os.system(restart_cmd)




def add_patch_callback(path='', tags='', args='', source=''):
    directory = os.path.dirname(os.path.realpath(__file__))
    patches_dir = os.path.join(directory, '../patches')
    if not args or len(args) < 2:
        print("/addpatch requires two arguments: user and repo")
        return
    user = str(args[0]).strip()
    repo = str(args[1]).strip()
    if not re.match(r'^[\w-]+$', user):
        print(f"Invalid user: {user}")
        return
    if not re.match(r'^[\w.-]+$', repo):
        print(f"Invalid repo: {repo}")
        return
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
    # Clone repo recursively (120s timeout to handle slow networks)
    try:
        print(f"Cloning {repo_url} into {dest_dir}...")
        result = subprocess.run(
            ["git", "clone", "--recursive", repo_url, dest_dir],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120
        )
        if result.returncode != 0:
            print(f"Failed to clone repo: {result.stderr.decode().strip()}")
            return
        print(f"Cloned {repo_url} into {dest_dir}")
    except subprocess.TimeoutExpired:
        print(f"Clone timed out after 120s — check network connection")
        return
    except Exception as e:
        print(f"Error cloning repo: {e}")
        return

    # Validate patch has a main.pd entrypoint
    if not os.path.isfile(os.path.join(dest_dir, 'main.pd')):
        print(f"Warning: cloned patch '{repo}' has no main.pd — it won't load in PD")

    # Send OSC confirmation
    try:
        msg = OSCMessage("/addpatch")
        msg.append(repo)
        client.send(msg)
    except Exception as e:
        print(f"Failed to send OSC confirmation: {e}")

# Pull the latest changes for the currently active patch repo
def pull_active_patch_callback(path='', tags='', args='', source=''):
    directory = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.join(directory, '../bash/pull_active_patch.sh')
    print(f"[pull_active_patch_callback] Running: {script_path}")
    try:
        result = subprocess.run(["bash", script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
        print("[pull_active_patch_callback] Output:")
        print(result.stdout.decode())
        if result.returncode != 0:
            print(f"[pull_active_patch_callback] Error: {result.stderr.decode()}")
        else:
            print("[pull_active_patch_callback] Patch updated successfully.")
    except Exception as e:
        print(f"[pull_active_patch_callback] Exception: {e}")


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
server.addMsgHandler( "/addpatch", add_patch_callback )  # expects two arguments: user, repo
server.addMsgHandler( "/pullpatch", pull_active_patch_callback )  # pulls the current active patch repo

atexit.register(exit_handler)

#ARG 1 MAC Address
if __name__ == "__main__":

    # config_callback()

    while True:
        sleep(1)
        server.handle_request()
