#!/bin/bash

# check current status
check_state() {
  if [[ "$(LANG=C LANGUAGE=C nmcli radio wifi)" == "enabled" ]];then
    echo "true"
  elif [[ "$(LANG=C LANGUAGE=C nmcli radio wifi)" == "disabled" ]];then
    echo "false"
  fi
}

# change the state
toggle_state() {
  new_state="$1"
  if [[ "$new_state" == "true" ]];then
    nmcli radio wifi on
    exitCode=$?
  else
    nmcli radio wifi off
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
