#!/bin/bash
package="biglinux-docker-nextcloud-plus"
packageName="nextcloud-plus"
port="8286"

if [ "$1" == "check" ]; then
    if pacman -Q "$package" &> /dev/null; then
        echo "true"
    else
        echo "false"
    fi
elif [ "$1" == "toggle" ]; then
    state="$2"
    if [ "$state" == "true" ]; then
      pkexec $PWD/docker/dockerInstallRun.sh "install" "$package" "$packageName" "$port" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    else
      pkexec $PWD/docker/dockerInstallRun.sh "remove" "$package" "$packageName" "$port" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    fi
    exit $?
fi
