#!/bin/bash
# Update APT Informations for "dynamic-motd"
# apt-get is very slow, so we put the value in ENV

NEED_UPGRADE=$(apt-get -qq --just-print dist-upgrade | cut -f 2 -d " " | sort -u | wc -l)
NOT_NEEDED=$(apt-get -qq --just-print autoremove | cut -f 2 -d " " | sort -u | wc -l)
if [ grep "NEED_UPGRADE" /etc/environment && grep "NOT_NEEDED" /etc/environment ]
then
    sed -i "s/^NEED_UPGRADE=.*/NEED_UPGRADE=$NEED_UPGRADE/" /etc/environment
    sed -i "s/^NOT_NEEDED=.*/NOT_NEEDED=$NOT_NEEDED/" /etc/environment
else
    printf "NEED_UPGRADE=$NEED_UPGRADE\n" >> /etc/environment
    printf "NOT_NEEDED=$NOT_NEEDED\n" >> /etc/environment
fi
