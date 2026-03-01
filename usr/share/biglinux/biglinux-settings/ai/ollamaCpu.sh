#!/bin/bash

#Translation
export TEXTDOMAINDIR="/usr/share/locale"
export TEXTDOMAIN=biglinux-settings

info() {
  zenityText=$"Ollama server is running.\nAddress: http://localhost:11434"
  zenity --info --text="$zenityText" --width=300 --height=200
}

# check current status
# action=$1
if [ "$1" == "check" ]; then
  if pacman -Q ollama &>/dev/null && ! pacman -Q ollama-vulkan &>/dev/null && ! pacman -Q ollama-rocm &>/dev/null && ! pacman -Q ollama-cuda &>/dev/null ; then
    echo "true"
  else
    echo "false"
  fi

# change the state
# action=$1
# state=$2
elif [ "$1" == "toggle" ]; then
  if [ "$2" == "true" ]; then
    pkexec $PWD/ai/ollamaCpuRun.sh "install" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    exitCode=$?
    info
  else
    pkexec $PWD/ai/ollamaCpuRun.sh "uninstall" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    exitCode=$?
  fi
  exit $exitCode
fi
