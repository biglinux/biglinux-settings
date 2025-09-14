#!/bin/bash

app='epiphany'
verifyApp='/usr/bin/epiphany'

# check current status
check_state() {
  if [[ -e "$verifyApp" ]];then
    if [[ -e "/etc/big-preload/enable-${app}" ]];then
      echo "true"
    else
      echo "false"
    fi
  else
    echo ""
  fi
}

# change the state
toggle_state() {
  new_state="$1"
  if [[ "$new_state" == "true" ]];then
      pkexec touch /etc/big-preload/enable-${app}
      exitCode=$?
  else
      pkexec rm -f /etc/big-preload/enable-${app}
      exitCode=$?
  fi
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
