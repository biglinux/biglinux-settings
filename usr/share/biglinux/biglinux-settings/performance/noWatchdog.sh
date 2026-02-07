#!/bin/bash

# check current status
if [ "$1" == "check" ]; then
  if [[ -n "$(grep "nowatchdog" /proc/cmdline)" ]] && [[ -n "$(grep "tsc=nowatchdog" /proc/cmdline)" ]];then
    echo "true"
  else
    echo "false"
  fi

# change the state
elif [ "$1" == "toggle" ]; then
  state="$2"
  if [ "$state" == "true" ]; then
    pkexec $PWD/performance/noWatchdogRun.sh "enable" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    exitCode=$?
  else
    pkexec $PWD/performance/noWatchdogRun.sh "disable" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    exitCode=$?
  fi
  exit $exitCode
fi
