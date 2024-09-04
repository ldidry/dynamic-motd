#!/usr/bin/python3
"""
landscape-sysinfo-mini.py -- a trivial re-implementation of the
sysinfo printout shown on debian at boot time. No twisted, no reactor, just /proc & utmp

(C) 2014 jw@owncloud.com

inspired by ubuntu 14.10 /etc/update-motd.d/50-landscape-sysinfo
Requires: python3-utmp
for counting users.

2014-09-07 V1.0 jw, ad hoc writeup, feature-complete. Probably buggy?
2014-10-08 V1.1 jw, survive without swap
2014-10-13 V1.2 jw, survive without network

Modified by Luc Didry in 2016 and 2023
Get the original version at https://github.com/jnweiger/landscape-sysinfo-mini
"""


import glob
import os
import subprocess
import sys
import time


def dev_addr(device):
    """find the local ip address on the given device"""
    if device is None:
        return None
    for l in os.popen("ip route list dev " + device):
        seen = ""
        for a in l.split():
            if seen == "src":
                return a
            seen = a
    return None


def default_dev():
    """find the device where our default route is"""
    for l in open("/proc/net/route").readlines():
        a = l.split()
        if a[1] == "00000000":
            return a[0]
    return None


def get_users():
    # Run the who command and capture its output
    who_output_list = subprocess.check_output(["who"]).decode("utf-8").split("\n")
    # Create a set to store unique usernames
    unique_users = set()

    # Iterate through each line and extract usernames
    for line in who_output_list:
        line_list = line.split()
        if bool(line_list):
            unique_users.add(line_list[0])

    # Join the unique usernames into a single string separated by commas
    result = ", ".join(unique_users)

    return result


def proc_meminfo():
    """ Get memory usage informations
    """
    items = {}
    for line in open('/proc/meminfo', encoding="ASCII").readlines():  # pylint: disable-msg=R1732
        array = line.split()
        items[array[0]] = int(array[1])
    return items

def proc_mount():
    """ Get disks space usage
    """
    items = {}
    for mount in open('/proc/mounts', encoding="ASCII").readlines():  # pylint: disable-msg=R1732
        array = mount.split()
        if array[0].find('/dev/') == 0:
            l_statfs = os.statvfs(array[1])
            perc = 100 - 100. * l_statfs.f_bavail / l_statfs.f_blocks \
                    if l_statfs.f_blocks != 0 else 100
            g_b = l_statfs.f_bsize * l_statfs.f_blocks / 1024. / 1024 / 1024
            items[array[1]] = f"{perc:5.1f}% of {g_b:.2f}GB"
    return items

def inode_proc_mount():
    """ Get disks inode usage
    """
    items = {}
    for mount in open('/proc/mounts', encoding="ASCII").readlines():  # pylint: disable-msg=R1732
        array = mount.split()
        if array[0].find('/dev/') == 0:
            l_statfs = os.statvfs(array[1])
            perc = 100 - 100. * l_statfs.f_ffree / l_statfs.f_files \
                    if l_statfs.f_files != 0 else 100
            i_total = l_statfs.f_files
            items[array[1]] = f"{perc:5.1f}% of {i_total}"
    return items

<<<<<<< HEAD
with open("/proc/loadavg", encoding="ASCII") as avg_line:
    loadav = float(avg_line.read().split()[1])
processes = len(glob.glob('/proc/[0-9]*'))
=======

ip_addr = dev_addr(default_dev())
>>>>>>> 5fa57c4 (Restore ip address)
statfs = proc_mount()
i_statfs = inode_proc_mount()
users = get_users()
meminfo = proc_meminfo()
memperc = f"{100 - 100. * meminfo['MemAvailable:'] / (meminfo['MemTotal:'] or 1):.2f}%"
SWAPPERC = f"{100 - 100. * meminfo['SwapFree:'] / (meminfo['SwapTotal:'] or 1):.2f}%"

if meminfo['SwapTotal:'] == 0:
    SWAPPERC = '---'

<<<<<<< HEAD
print(f"  System information as of {time.asctime()}\n")
print(f"  System load:  {loadav: <5.2f}                Processes:           {processes}")
print(f"  Memory usage: {memperc: <4}               Users logged in:     {USERS}")
print(f"  Swap usage:   {SWAPPERC}")
=======
print(
    """
System information as of %s on %s
"""
    % (time.asctime(), ip_addr)
)
>>>>>>> 5fa57c4 (Restore ip address)

print("  Disk Usage:")
for k in sorted(statfs.keys()):
    print(f"    Usage of {k: <24}: {statfs[k]: <20}")

print("  Inode Usage:")
for l in sorted(i_statfs.keys()):
    print(f"    Usage of {l: <24}: {i_statfs[l]: <20}")

    if users != "":
        print(
            f"""
   Logged in users: {users}
"""
        )

sys.exit(0)
