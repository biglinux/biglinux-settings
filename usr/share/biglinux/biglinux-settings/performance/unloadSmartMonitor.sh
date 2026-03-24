#!/bin/bash

#Translation
export TEXTDOMAINDIR="/usr/share/locale"
export TEXTDOMAIN=biglinux-settings

# check current status
# action=$1
if [ "$1" == "check" ]; then
  # Check if it's a VM; if so, disable it. Smart only works on a physical machine.
  if [[ "$(systemd-detect-virt)" != "none" ]];then
    echo ""
  elif systemctl is-active smartd --quiet;then
    echo "false"
  else
    echo "true"
  fi

# change the state
# action=$1
# state=$2
elif [ "$1" == "toggle" ]; then
  if [ "$2" == "true" ]; then
    systemctl disable --now smartd
  else
    systemctl enable --now smartd
  fi
  exit $?
fi
