#!/bin/bash

# check current status
if [ "$1" == "check" ]; then
  if [[ "$(grep '@audio' /etc/security/*.conf | grep rtprio | awk '{print $4}')" -ge "90" ]] && [[ -n "$(grep 'memlock.*unlimited' /etc/security/*.conf)" ]];then
    echo "true"
  else
    echo "false"
  fi

# change the state
elif [ "$1" == "toggle" ]; then
  state="$2"
  if [ "$state" == "true" ]; then
    pkexec $PWD/system/limitsRun.sh "enable" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    exitCode=$?
  else
    pkexec $PWD/system/limitsRun.sh "disable" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    exitCode=$?
  fi
  exit $exitCode
fi
