#!/bin/bash

# check current status
check_state() {
  if [[ "$(systemctl is-enabled docker)" == "enabled" ]] && [[ "$(systemctl is-active docker)" == "active" ]];then
    echo "true"
  else
    echo "false"
  fi
}

# change the state
toggle_state() {
  new_state="$1"
  if [[ "$new_state" == "true" ]];then
    if pacman -Q biglinux-docker-config &>/dev/null; then
      pkexec $PWD/system/dockerEnableRun.sh "install" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    fi
      pkexec systemctl enable docker
      exitCode=$?
  else
      pkexec systemctl disable docker
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
