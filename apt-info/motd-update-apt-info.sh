#!/bin/bash
# Update APT Informations for "dynamic-motd"
# apt-get is very slow, so we put the value in ENV

MOTD_NEED_UPGRADE=$(apt-get -qq --just-print dist-upgrade | cut -f 2 -d " " | sort -u | wc -l)
MOTD_NOT_NEEDED=$(apt-get -qq --just-print autoremove | cut -f 2 -d " " | sort -u | wc -l)
if [ grep "MOTD_NEED_UPGRADE" /etc/environment && grep "MOTD_NOT_NEEDED" /etc/environment ]
then
    sed -i "s/^MOTD_NEED_UPGRADE=.*/MOTD_NEED_UPGRADE=$MOTD_NEED_UPGRADE/" /etc/environment
    sed -i "s/^MOTD_NOT_NEEDED=.*/MOTD_NOT_NEEDED=$MOTD_NOT_NEEDED/" /etc/environment
else
    printf "MOTD_NEED_UPGRADE=$MOTD_NEED_UPGRADE\n" >> /etc/environment
    printf "MOTD_NOT_NEEDED=$MOTD_NOT_NEEDED\n" >> /etc/environment
fi
