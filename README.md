# Dynamic motd

The aim of this project is to give some informations when you log into a server through SSH.

Example:

```

   ___  ___ _ ____   _____ _ __
  / __|/ _ \ '__\ \ / / _ \ '__|
  \__ \  __/ |   \ V /  __/ |
  |___/\___|_|    \_/ \___|_|


  Debian GNU/Linux 12 (bookworm) (kernel 6.1.0-7-amd64)

System information as of Fri Sep  6 10:26:52 2024 on 192.168.1.20

System load:  0.01                 Processes:    211
Memory usage: 24.40%               Swap usage:   0.02%

  Mount points          Disk usage        Inodes usage
 /                     18%  of 14G       8.7% of 938400
 /boot                 8%   of 1.8G      0.0% of 999936
 /boot/efi             1%   of 974.1M    Not available
 /opt                  3%   of 4.6G      0.0% of 312624
 /var                  13%  of 4.6G      1.4% of 312624
 /var/log              2%   of 4.6G      0.0% of 312624
 /var/log/audit        0%   of 4.6G      0.0% of 312624
 /var/tmp              0%   of 4.6G      0.0% of 312624

       Logged in users: admin


No mail.
Last login: Mon Apr  3 07:28:01 2023 from laptop.example.org
```

**Warning** This is Debian and Debian-related distributions only.

## Installation

### Debian package

Go to <https://framagit.org/luc/dynamic-motd/-/releases/permalink/latest>, download the Debian package and its signature file.

Check the signature of the Debian package and install the package:
```bash
minisign -Vm dynamic-motd_*.deb -P RWRzxrp04vb4Db3sle7Az6kSeCipT1ixRjRZPXdUUQuuwgi9UW81E+dx &&
sudo apt install ./dynamic-motd_*.deb
```

### Manual installation

You need to install some packages:

```
apt-get install figlet lsb-release bc
```

Optionally, you can install `needrestart` which is used to show a message if your server need a reboot (main reason (and the only one I know): you have upgraded your kernel).
If you don't install `needrestart`, it will work, but you won't be warned about the need for a reboot.
`needrestart` warns you about services that need to be restarted too (but is slower than `checkrestart` for that, see below).

You can optionally install `debian-goodies` which provides `checkrestart`, which will be used to warn you about services that need to be restarted. Relying on `needrestart` for that is slow (±7 seconds) while `checkrestart` do it faster (less than one second).

Check out the repo (to a folder of your choice)
```
git clone https://framagit.org/luc/dynamic-motd.git
cd dynamic-motd/
```

Then, as `root`:
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
