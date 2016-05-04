motd-packages:
  pkg.installed:
    - pkgs:
      - figlet
      - lsb-release
      - python-utmp
      - bc
needrestart:
  pkg.installed:
    - pkgs:
      - needrestart
symbolic-motd:
  file.symlink:
    - name: /etc/motd
    - target: /var/run/motd
    - force: True
    - backupname: Truek
dynamic-motd:
  file.recurse:
    - name: /etc/update-motd.d/
    - source: salt://motd/update-motd.d/
    - file_mode: 755
remove-exec-colors:
  file.managed:
    - name: /etc/update-motd.d/colors
    - mode: 644
remove-exec-sysinfo:
  file.managed:
    - name: /etc/update-motd.d/sysinfo.py
    - mode: 644
