#!/usr/bin/python3
#
# landscape-sysinfo-mini.py -- a trivial re-implementation of the
# sysinfo printout shown on debian at boot time. No twisted, no reactor, just /proc & utmp
#
# (C) 2014 jw@owncloud.com https://github.com/jnweiger/landscape-sysinfo-mini
# (C) 2016 Luc Didry https://github.com/ldidry/dynamic-motd/blob/master/update-motd.d/sysinfo.py
# (C) 2024 seven-beep@entreparentheses.xyz
#
# inspired by ubuntu 14.10 /etc/update-motd.d/50-landscape-sysinfo
#
# 2014-09-07 V1.0 -- jw, ad hoc writeup, feature-complete. Probably buggy?
# 2014-10-08 V1.1 -- jw, survive without swap
# 2014-10-13 V1.2 -- jw, survive without network
# 2016            -- Luc Didry
# 2024-09-04 V1.3 -- 7b, remove dependance on utmp, rework disk usage, add error
# handling, change spacing, restore ip address.

import glob
import json
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
    items = {}
    for l in open("/proc/meminfo").readlines():
        a = l.split()
        items[a[0]] = int(a[1])
    # print items['MemTotal:'], items['MemFree:'], items['SwapTotal:'], items['SwapFree:']
    return items


def get_filesystems():
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

    loadav = float(open("/proc/loadavg").read().split()[1])
    processes = len(glob.glob("/proc/[0-9]*"))
    meminfo = proc_meminfo()
    filesystems = get_filesystems()
    ip_addr = dev_addr(default_dev())
    memperc = "%d%%" % (
        100 - 100.0 * meminfo["MemAvailable:"] / (meminfo["MemTotal:"] or 1)
    )
    swapperc = "%d%%" % (
        100 - 100.0 * meminfo["SwapFree:"] / (meminfo["SwapTotal:"] or 1)
    )
    users = get_users()

    if meminfo["SwapTotal:"] == 0:
        swapperc = "---"

    print(
        """
System information as of %s on %s
"""
        % (time.asctime(), ip_addr)
    )

    print("System load:  %-5.2f                Processes:    %d" % (loadav, processes))
    print("Memory usage: %-4s                 Swap usage:   %s" % (memperc, swapperc))

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
