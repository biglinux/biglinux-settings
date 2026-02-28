#!/bin/bash

# check current status
# action=$1
if [ "$1" == "check" ]; then
  if [[ "$(systemctl is-enabled docker)" == "enabled" ]] && [[ "$(systemctl is-active docker)" == "active" ]] && [[ "$(systemctl is-active docker.socket)" == "active" ]];then
    echo "true"
  else
    echo "false"
  fi

# change the state
# action=$1
# state=$2
elif [ "$1" == "toggle" ]; then
  if [ "$2" == "true" ]; then
    if ! pacman -Q biglinux-docker-config &>/dev/null; then
      pkexec $PWD/docker/dockerEnableRun.sh "install" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    else
      pkexec $PWD/docker/dockerEnableRun.sh "enable" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    fi
  else
    pkexec $PWD/docker/dockerEnableRun.sh "disable" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
  fi
  exit $?
fi
