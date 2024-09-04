# Dynamic motd

The aim of this project is to give some informations when you log into a server through SSH.

Example:

```

   ___  ___ _ ____   _____ _ __
  / __|/ _ \ '__\ \ / / _ \ '__|
  \__ \  __/ |   \ V /  __/ |
  |___/\___|_|    \_/ \___|_|


  Debian GNU/Linux 8.4 (jessie) (kernel 3.16.0-4-amd64)


  System information as of Fri Apr 22 10:02:57 2016

  System load:  2.74                 Processes:           167
  Memory usage: 98%                  Users logged in:     1
  Swap usage:   31%
  Disk Usage:
    Usage of /                       : 37.0% of 19.18GB
    Usage of /boot                   : 36.6% of 0.11GB
    Usage of /home                   : 11.1% of 501.60GB
  Inode Usage:
    Usage of /                       : 12.7% of 1286144
    Usage of /boot                   : 1.1% of 31232
    Usage of /home                   : 0.1% of 33406976

  Logged in users:
  user       from laptop.example.org        at Fri Apr 22 09:09:09 2016

No mail.
Last login: Fri Apr 22 09:23:01 2016 from laptop.example.org
```

**Warning** This is Debian and Debian-related distributions only.

## Dependencies

You need to install some packages:

```
apt-get install figlet lsb-release bc
```

Optionnally, you can install `needrestart` which is used to show a message if your server need a reboot (main reason (and the only one I know): you have upgraded your kernel).
If you don't install `needrestart`, it will work, but you won't be warned about the need for a reboot.
`needrestart` warns you about services that need to be restarted too (but is slower than `checkrestart` for that, see below).

You can optionnally install `debian-goodies` which provides `checkrestart`, which will be used to warn you about services that need to be restarted. Relying on `needrestart` for that is slow (±7 seconds) while `checkrestart` do it faster (less than one second).


## Installation

```
cp -r update-motd.d/ /etc
rm /etc/motd
ln -s /var/run/motd /etc/motd
```

## Disabling for some users

Just create a `/etc/update-motd.d/hushlogin` file containing the names of the users, like:

```
alice
bob
```

## Salt

You will find a working salt formula in `init.sls`.

```
cd /srv/salt
git clone https://framagit.org/luc/dynamic-motd.git motd
salt your_server state.sls motd
```

## License

GPLv2. Have a look at the [LICENSE file](LICENSE).

## Acknowledments

- Dustin Kirkland, the guy behind the Ubuntu dynamic motd (I took some scripts from Ubuntu and stole inspiration too :D)
- https://github.com/maxis1718/update-motd.d for the skeleton
- https://github.com/jnweiger/landscape-sysinfo-mini for the python script (slightly modified)
