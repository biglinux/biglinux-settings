#!/bin/bash

# check current status
check_state() {
  bluetoothState="$(LANG=C LANGUAGE=C timeout 0.1 bluetoothctl show | grep "Powered:" | awk '{print $2}')"
  if [[ "$bluetoothState" == "yes" ]];then
    echo "true"
  elif [[ "$bluetoothState" == "no" ]];then
    echo "false"
  fi
}

# change the state
toggle_state() {
  new_state="$1"
  if [[ "$new_state" == "true" ]];then
    timeout 2 bluetoothctl power on
    exitCode=$?
  else
    timeout 2 bluetoothctl power off
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
