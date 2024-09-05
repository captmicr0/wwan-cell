#!/bin/sh
### Post-installs setup
### for my cellular WWAN bridge VM
### running on Alpine Linux V3.17

../alpine-common.sh

# Setup edge repos
echo "https://dl-cdn.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories
echo "https://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories

# Ensure no MM / NM
apk del modemmanager
apk del networkmanager

# Update & Upgrade
apk update
apk upgrade

# Make sure using LTS kernel and not VIRT
apk add linux-lts
apk del linux-virt

# Add MBIM packages
apk add libmbim
apk add libmbim-tools

# Setup modem
mbimcli --device=/dev/cdc-wdm0 --device-open-proxy --query-device-caps

# Make sure you place connect and mbim-set-ip in /home directory
# Make scripts executable
chmod +x /home/connect
chmod +x /home/mbim-set-ip

# Link 'connect' to local.d to run on startup

ln -s /home/connect /etc/local.d/modem_init.start
