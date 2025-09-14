#!/bin/bash

# check current status
check_state() {
  if [[ "$(grep '@audio' /etc/security/*.conf | grep rtprio | awk '{print $4}')" -ge "90" ]] && [[ -n "$(grep 'memlock.*unlimited' /etc/security/*.conf)" ]];then
    echo "true"
  else
    echo "false"
  fi
}

# change the state
toggle_state() {
  new_state="$1"
  if [[ "$new_state" == "true" ]];then
    pkexec $PWD/system/limitsRun.sh "enable" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    exitCode=$?
  else
    pkexec $PWD/system/limitsRun.sh "disable" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
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
