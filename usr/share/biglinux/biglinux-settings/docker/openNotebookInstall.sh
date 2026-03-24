#!/bin/bash
package="biglinux-docker-open-notebook"
packageName="open-notebook"
port="8502"

# check current status
# action=$1
if [ "$1" == "check" ]; then
  if pacman -Q "$package" &> /dev/null; then
      echo "true"
  else
      echo "false"
  fi

# change the state
# action=$1
# state=$2
elif [ "$1" == "toggle" ]; then
  if [ "$2" == "true" ]; then
    pkexec $PWD/docker/dockerInstallRun.sh "install" "$package" "$packageName" "$port" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
  else
    pkexec $PWD/docker/dockerInstallRun.sh "remove" "$package" "$packageName" "$port" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
  fi
  exit $?
fi
