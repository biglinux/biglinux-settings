#!/bin/bash

# check current status
if [ "$1" == "check" ]; then
  if [[ "$(grep GRUB_TIMEOUT= /etc/default/grub | cut -d"=" -f2)" == "1" ]];then
    echo "true"
  else
    echo "false"
  fi

# change the state
elif [ "$1" == "toggle" ]; then
  state="$2"
  if [ "$state" == "true" ]; then
    pkexec /usr/share/biglinux/biglinux-settings/system/fastGrubRun.sh "1" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    exitCode=$?
  else
    pkexec /usr/share/biglinux/biglinux-settings/system/fastGrubRun.sh "5" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    exitCode=$?
  fi
  exit $exitCode
fi
