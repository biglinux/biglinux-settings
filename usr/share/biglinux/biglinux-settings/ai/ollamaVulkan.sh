#!/bin/bash

#Translation
export TEXTDOMAINDIR="/usr/share/locale"
export TEXTDOMAIN=biglinux-settings

info() {
  zenityText=$"Ollama server is running.\nAddress: http://localhost:11434"
  zenity --info --text="$zenityText" --width=300 --height=200
}

# check current status
if [ "$1" == "check" ]; then
  if pacman -Q ollama-vulkan &>/dev/null; then
    echo "true"
  else
    echo "false"
  fi

# change the state
elif [ "$1" == "toggle" ]; then
  state="$2"
  if [ "$state" == "true" ]; then
    pkexec $PWD/ai/ollamaVulkanRun.sh "install" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    info
    exitCode=$?
  else
    pkexec $PWD/ai/ollamaVulkanRun.sh "uninstall" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    exitCode=$?
  fi
  exit $exitCode
fi
