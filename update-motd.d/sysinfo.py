#!/usr/bin/python3
"""
landscape-sysinfo-mini.py -- a trivial re-implementation of the
sysinfo printout shown on debian at boot time. No twisted, no reactor, just /proc & utmp

(C) 2014 jw@owncloud.com https://github.com/jnweiger/landscape-sysinfo-mini
(C) 2016, 2023 Luc Didry https://github.com/ldidry/dynamic-motd/blob/master/update-motd.d/sysinfo.py
(C) 2024 seven-beep@entreparentheses.xyz

inspired by ubuntu 14.10 /etc/update-motd.d/50-landscape-sysinfo

2014-09-07 V1.0 -- jw, ad hoc writeup, feature-complete. Probably buggy?
2014-10-08 V1.1 -- jw, survive without swap
2014-10-13 V1.2 -- jw, survive without network
2016, 2023      -- Luc Didry
2024-09-04 V1.3 -- 7b, remove dependance on utmp, rework disk usage, add error
handling, change spacing...
2025-09-25 V1.4 -- 7b, timeout on filesystem scan
"""

import functools
import glob
import json
import os
import signal
import subprocess
import sys
import time

import utmp


class TimeoutError(Exception):
    pass


def timeout(seconds, default=None):
    """Timeout decorator, parameter in seconds."""

    def timeout_decorator(func):
        """Wrap the original function."""

        @functools.wraps(func)
        def func_wrapper(*args, **kwargs):
            """Timeout using signal."""

            def handler(signum, frame):
                raise TimeoutError(
                    "{0}: {1} - Timeout after {2} seconds".format(
                        __file__, func.__name__, seconds
                    )
                )

            # Set the timeout handler.
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds)
            result = default
            try:
                result = func(*args, **kwargs)
            except TimeoutError as exc:
                # Handle the timeout.
                print(str(exc))
            finally:
                # Cancel the timer.
                signal.alarm(0)
            return result

        return func_wrapper

    return timeout_decorator


def utmp_count():
    """Count user processes"""
    l_users = 0
    for i in utmp.UtmpRecord():
        if i.ut_type == utmp.USER_PROCESS:
            l_users += 1
    return l_users


def proc_meminfo():
    """Get memory usage informations"""
    items = {}
    for line in open(
        "/proc/meminfo", encoding="ASCII"
    ).readlines():  # pylint: disable-msg=R1732
        array = line.split()
        items[array[0]] = int(array[1])
    return items


@timeout(2)
def get_filesystems():
    """Get the real filesystem monted informations."""
    filesystems = json.loads(
        subprocess.check_output(
            [
                "findmnt",
                "--noheading",
                "--real",
                "--uniq",
                "--json",
                "--types",
                "notmpfs,noswap,nodevtmpfs,noxenfs",
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

    logged_users = utmp_count()
    with open("/proc/loadavg", encoding="ASCII") as avg_line:
        loadav = float(avg_line.read().split()[1])
    processes = len(glob.glob("/proc/[0-9]*"))
    meminfo = proc_meminfo()
    memperc = "%d%%" % (
        100 - 100.0 * meminfo["MemAvailable:"] / (meminfo["MemTotal:"] or 1)
    )
    swapperc = "%d%%" % (
        100 - 100.0 * meminfo["SwapFree:"] / (meminfo["SwapTotal:"] or 1)
    )

    if meminfo["SwapTotal:"] == 0:
        swapperc = "---"

    print("System information as of %s\n" % time.asctime())
    print("System load:  %-5.2f                Processes:    %d" % (loadav, processes))
    print("Memory usage: %-4s                 Swap usage:   %s" % (memperc, swapperc))

    filesystems = get_filesystems()
    if filesystems:
        print(
            """
   Mount points                       Disk usage        Inodes usage"""
        )
        for f in filesystems:
            print(
                " %-35s %-4s of %-9s %s"
                % (f["target"], f["use%"], f["size"], f["inodes%"])
            )

    if logged_users > 0:
        a = utmp.UtmpRecord()
        print(f"\n  {logged_users} logged in users:")
        for b in a:
            if b.ut_type == utmp.USER_PROCESS:
                print(
                    f"  \033[1;31m{b.ut_user: <10}\033[m from {b.ut_host: <25}"
                    f" at {time.ctime(b.ut_tv[0]): <20}"
                )
        a.endutent()

    sys.exit(0)


if __name__ == "__main__":
    main()
