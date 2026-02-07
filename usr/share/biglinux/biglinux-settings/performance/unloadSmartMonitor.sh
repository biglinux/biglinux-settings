#!/bin/bash

#Translation
export TEXTDOMAINDIR="/usr/share/locale"
export TEXTDOMAIN=biglinux-settings

# check current status
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
elif [ "$1" == "toggle" ]; then
  state="$2"
  if [ "$state" == "true" ]; then
    systemctl disable --now smartd
    exitCode=$?
  else
    systemctl enable --now smartd
    exitCode=$?
  fi
  exit $exitCode
fi
