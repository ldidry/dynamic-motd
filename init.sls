motd-packages:
  pkg.installed:
    - pkgs:
      - figlet
      - lsb-release
{% if grains["oscodename"] == 'bullseye' %}
      - python3-utmp
{% else %}
      - python-utmp
{% endif %}
      - bc
      - debian-goodies
needrestart:
  pkg.installed:
    - pkgs:
      - needrestart
symbolic-motd:
  file.symlink:
    - name: /etc/motd
    - target: /var/run/motd
    - force: True
    - backupname: bak
dynamic-motd:
  file.recurse:
    - name: /etc/update-motd.d/
    - source: salt://motd/update-motd.d/
    - file_mode: 755
    # If you installed this motd prior to commit 7bae3d50,
    # you may want to enable the clean option in order to
    # remove the old files (01-*, 02-*, etc) since they have
    # been renumbered. Be careful! If you added some files of
    # yours, they will be deleted
    #- clean: True
{% if grains["oscodename"] == 'bullseye' %}
/etc/update-motd.d/20-system-info:
  file.replace:
    - pattern: 'python'
    - repl: 'python3'
/etc/update-motd.d/sysinfo.py:
  file.replace:
    - pattern: 'python'
    - repl: 'python3'
{% endif %}
remove-exec-colors:
  file.managed:
    - name: /etc/update-motd.d/colors
    - mode: 644
remove-exec-quiet:
  file.managed:
    - name: /etc/update-motd.d/quiet
    - mode: 644
remove-exec-sysinfo:
  file.managed:
    - name: /etc/update-motd.d/sysinfo.py
    - mode: 644
