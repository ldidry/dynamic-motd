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
import os
import posix
import sys
import time

import utmp
from UTMPCONST import *

_version_ = "1.2"


def utmp_count():
    u = utmp.UtmpRecord()
    users = 0
    for i in u:
        if i.ut_type == utmp.USER_PROCESS:
            users += 1
    return users


def proc_meminfo():
    items = {}
    for l in open("/proc/meminfo").readlines():
        a = l.split()
        items[a[0]] = int(a[1])
    # print items['MemTotal:'], items['MemFree:'], items['SwapTotal:'], items['SwapFree:']
    return items


def proc_mount():
    items = {}
    for m in open("/proc/mounts").readlines():
        a = m.split()
        if a[0].find("/dev/") == 0:
            statfs = os.statvfs(a[1])
            perc = (
                100 - 100.0 * statfs.f_bavail / statfs.f_blocks
                if statfs.f_blocks != 0
                else 100
            )
            gb = statfs.f_bsize * statfs.f_blocks / 1024.0 / 1024 / 1024
            items[a[1]] = "%.1f%% of %.2fGB" % (perc, gb)
    return items


def inode_proc_mount():
    items = {}
    for m in open("/proc/mounts").readlines():
        a = m.split()
        if a[0].find("/dev/") == 0:
            statfs = os.statvfs(a[1])
            perc = (
                100 - 100.0 * statfs.f_ffree / statfs.f_files
                if statfs.f_files != 0
                else 100
            )
            iTotal = statfs.f_files
            items[a[1]] = "%.1f%% of %.2d" % (perc, iTotal)
    return items


loadav = float(open("/proc/loadavg").read().split()[1])
processes = len(glob.glob("/proc/[0-9]*"))
statfs = proc_mount()
iStatfs = inode_proc_mount()
users = utmp_count()
meminfo = proc_meminfo()
memperc = "%d%%" % (
    100 - 100.0 * meminfo["MemAvailable:"] / (meminfo["MemTotal:"] or 1)
)
swapperc = "%d%%" % (100 - 100.0 * meminfo["SwapFree:"] / (meminfo["SwapTotal:"] or 1))

if meminfo["SwapTotal:"] == 0:
    swapperc = "---"

print("  System information as of %s\n" % time.asctime())
print(
    "  System load:  %-5.2f                Processes:           %d"
    % (loadav, processes)
)
print("  Memory usage: %-4s                 Users logged in:     %d" % (memperc, users))
print("  Swap usage:   %s" % (swapperc))

print("  Disk Usage:")
for k in sorted(statfs.keys()):
    print("    Usage of %-24s: %-20s" % (k, statfs[k]))

print("  Inode Usage:")
for l in sorted(iStatfs.keys()):
    print("    Usage of %-24s: %-20s" % (l, iStatfs[l]))

if users > 0:
    a = utmp.UtmpRecord()

    print("\n  Logged in users:")

    for b in a:  # example of using an iterator
        if b.ut_type == USER_PROCESS:
            print(
                "  \033[1;31m%-10s\033[m from %-25s at %-20s"
                % (b.ut_user, b.ut_host, time.ctime(b.ut_tv[0]))
            )
    a.endutent()

sys.exit(0)
