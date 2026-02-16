#!/bin/bash

#Translation
export TEXTDOMAINDIR="/usr/share/locale"
export TEXTDOMAIN=biglinux-settings

# check current status
if [ "$1" == "check" ]; then
  if [ -d "$HOME/ComfyUI" ]; then
    echo "true"
  else
    echo "false"
  fi

# change the state
elif [ "$1" == "toggle" ]; then
  state="$2"
  if [ "$state" == "true" ]; then
    if ! pacman -Q python-pip &>/dev/null || ! pacman -Q git &>/dev/null; then
      pkexec $PWD/ai/comfyUIDepends.sh "install" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    fi
    $PWD/ai/comfyUIInstall.sh "install"
    exitCode=$?
  else
    $PWD/ai/comfyUIInstall.sh "uninstall"
    exitCode=$?
  fi
  exit $exitCode
fi
