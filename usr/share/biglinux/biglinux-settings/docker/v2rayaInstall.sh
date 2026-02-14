#!/bin/bash
package="biglinux-docker-v2raya"
packageName="v2raya"
port="2017"

# check current status
if [ "$1" == "check" ]; then
  if pacman -Q "$package" &> /dev/null; then
      echo "true"
  else
      echo "false"
  fi

# change the state
elif [ "$1" == "toggle" ]; then
  state="$2"
  if [ "$state" == "true" ]; then
    pkexec $PWD/docker/dockerInstallRun.sh "install" "$package" "$packageName" "$port" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    exit $exitCode
  else
    pkexec $PWD/docker/dockerInstallRun.sh "remove" "$package" "$packageName" "$port" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    exit $exitCode
  fi
  exit $?
fi
