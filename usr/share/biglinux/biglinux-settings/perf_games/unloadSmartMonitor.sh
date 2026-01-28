#!/bin/bash

#Translation
export TEXTDOMAINDIR="/usr/share/locale"
export TEXTDOMAIN=biglinux-settings

# check current status
check_state() {
  # Check if it's a VM; if so, disable it. Smart only works on a physical machine.
  if [[ "$(systemd-detect-virt)" != "none" ]];then
    echo ""
  elif systemctl is-active smartd --quiet;then
    echo "false"
  else
    echo "true"
  fi
}

# change the state
toggle_state() {
  new_state="$1"
  if [[ "$new_state" == "true" ]];then
    systemctl disable --now smartd
    exitCode=$?
  else
    systemctl enable --now smartd
    exitCode=$?
  fi
  exit $exitCode
}

# Executes the function based on the parameter
case "$1" in
    "check")
        check_state
        ;;
    "toggle")
        toggle_state "$2"
        ;;
    *)
        echo "Use: $0 {check|toggle} [true|false]"
        echo "  check          - Check current status"
        echo "  toggle <state> - Changes to the specified state"
        exit 1
        ;;
esac
