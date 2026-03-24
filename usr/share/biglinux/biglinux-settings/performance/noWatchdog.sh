#!/bin/bash

# check current status
# action=$1
if [ "$1" == "check" ]; then
  if [[ -n "$(grep "nowatchdog" /proc/cmdline)" ]] && [[ -n "$(grep "tsc=nowatchdog" /proc/cmdline)" ]] && [[ -n "$(grep "nowatchdog" /etc/default/grub)" ]] && [[ -n "$(grep "tsc=nowatchdog" /etc/default/grub)" ]] ;then
    echo "true"
  else
    echo "false"
  fi

# change the state
# action=$1
# state=$2
elif [ "$1" == "toggle" ]; then
  if [ "$2" == "true" ]; then
    pkexec $PWD/performance/noWatchdogRun.sh "enable" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
  else
    pkexec $PWD/performance/noWatchdogRun.sh "disable" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
  fi
  exit $?
fi
