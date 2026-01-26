#!/bin/bash
PACKAGE="biglinux-docker-lamp"

if [ "$1" == "check" ]; then
    if pacman -Q "$PACKAGE" &> /dev/null; then
        echo "true"
    else
        echo "false"
    fi
elif [ "$1" == "toggle" ]; then
    STATE="$2"
    if [ "$STATE" == "true" ]; then
      ACTION="install"
    else
      ACTION="remove"
    fi
    pkexec $PWD/docker/dockerInstallRun.sh "$ACTION" "$PACKAGE" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    exit $?
fi
