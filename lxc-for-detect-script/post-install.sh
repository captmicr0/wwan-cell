#!/bin/sh
### Post-installs setup
### for my python scripts LXC
### running on Alpine Linux V3.17

../alpine-common.sh

# Install python & pip
apk add python3
apk add py3-pip

#Install pip modules
pip install pprint
pip install proxmoxer
pip install requests
pip install json
