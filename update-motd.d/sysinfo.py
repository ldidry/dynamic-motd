#!/usr/bin/python3
"""
landscape-sysinfo-mini.py -- a trivial re-implementation of the
sysinfo printout shown on debian at boot time. No twisted, no reactor, just /proc & utmp

(C) 2014 jw@owncloud.com
https://github.com/jnweiger/landscape-sysinfo-mini

inspired by ubuntu 14.10 /etc/update-motd.d/50-landscape-sysinfo

2014-09-07 V1.0 jw, ad hoc writeup, feature-complete. Probably buggy?
2014-10-08 V1.1 jw, survive without swap
2014-10-13 V1.2 jw, survive without network

Modified by Luc Didry in 2016 and 2023
https://github.com/ldidry/dynamic-motd

Modified by seven-beep@entreparentheses.xyz in 2024.
"""


import glob
import json
import os
import subprocess
import sys
import time


def get_ip_addr():
    """Find the local ip address on the given device"""
    ip_output_list = (
        subprocess.check_output(["hostname", "-I"]).decode("utf-8").split(" ")
    )

    if bool(ip_output_list):
        return ip_output_list[0]


def get_users():
    """Get the users connected on this machine."""
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
    """Get memory usage informations"""
    items = {}
    for line in open(
        "/proc/meminfo", encoding="ASCII"
    ).readlines():  # pylint: disable-msg=R1732
        array = line.split()
        items[array[0]] = int(array[1])
    return items


def get_filesystems():
    """Get the real filesystem information for all entries in /etc/fstab."""
    # Only using fstab values to filter the mess that can be containerisation or bind mounts.
    filesystems = json.loads(
        subprocess.check_output(
            [
                "findmnt",
                "--noheading",
                "--real",
                "--uniq",
                "--fstab",
                "--json",
                "--types",
                "notmpfs,noswap",
                "--df",
            ]
        )
    ).get("filesystems")

    for f in filesystems:
        try:
            statfs = os.statvfs(f["target"])

            perc = (
                100 - 100.0 * statfs.f_ffree / statfs.f_files
                if statfs.f_blocks != 0
                else 100
            )
            iTotal = statfs.f_files
            f["inodes%"] = "%.1f%% of %.2d" % (perc, iTotal)
        except PermissionError:
            f["inodes%"] = "Permission Denied"
        except FileNotFoundError:
            f["inodes%"] = "File not found"
        except ZeroDivisionError:
            f["inodes%"] = "Not available"

    return filesystems


def main():

    with open("/proc/loadavg", encoding="ASCII") as avg_line:
        loadav = float(avg_line.read().split()[1])
    processes = len(glob.glob("/proc/[0-9]*"))

    ip_addr = get_ip_addr()
    filesystems = get_filesystems()
    users = get_users()
    meminfo = proc_meminfo()
    memperc = (
        f"{100 - 100. * meminfo['MemAvailable:'] / (meminfo['MemTotal:'] or 1):.2f}%"
    )
    SWAPPERC = (
        f"{100 - 100. * meminfo['SwapFree:'] / (meminfo['SwapTotal:'] or 1):.2f}%"
    )

    if meminfo["SwapTotal:"] == 0:
        SWAPPERC = "---"

    print(
        """
System information as of %s on %s
    """
        % (time.asctime(), ip_addr)
    )

    print("System load:  %-5.2f                Processes:    %d" % (loadav, processes))
    print("Memory usage: %-7s              Swap usage:   %s" % (memperc, SWAPPERC))

    print(
        """
  Mount points          Disk usage        Inodes usage"""
    )

    for f in filesystems:
        print(
            " %-21s %-4s of %-9s %s" % (f["target"], f["use%"], f["size"], f["inodes%"])
        )

    if users != "":
        print(
            f"""
       Logged in users: {users}
    """
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
