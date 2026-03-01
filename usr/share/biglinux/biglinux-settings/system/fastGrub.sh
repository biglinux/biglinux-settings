#!/bin/bash

# check current status
# action=$1
if [ "$1" == "check" ]; then
  if [[ "$(grep GRUB_TIMEOUT= /etc/default/grub | cut -d"=" -f2)" == "1" ]];then
    echo "true"
  else
    echo "false"
  fi

# change the state
# action=$1
# state=$2
elif [ "$1" == "toggle" ]; then
  if [ "$2" == "true" ]; then
    pkexec /usr/share/biglinux/biglinux-settings/system/fastGrubRun.sh "1" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
  else
    pkexec /usr/share/biglinux/biglinux-settings/system/fastGrubRun.sh "5" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
  fi
  exit $?
fi
