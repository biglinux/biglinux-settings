#!/bin/bash

# check current status
if [ "$1" == "check" ]; then
  if [[ "$(systemctl is-enabled docker)" == "enabled" ]] && [[ "$(systemctl is-active docker)" == "active" ]] && [[ "$(systemctl is-active docker.socket)" == "active" ]];then
    echo "true"
  else
    echo "false"
  fi

# change the state
elif [ "$1" == "toggle" ]; then
  state="$2"
  if [ "$state" == "true" ]; then
    if ! pacman -Q biglinux-docker-config &>/dev/null; then
      pkexec $PWD/docker/dockerEnableRun.sh "install" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    else
      pkexec $PWD/docker/dockerEnableRun.sh "enable" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    fi
    exitCode=$?
  else
    pkexec $PWD/docker/dockerEnableRun.sh "disable" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    exitCode=$?
  fi
  exit $exitCode
fi
