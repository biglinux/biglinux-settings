#!/bin/bash

#Translation
export TEXTDOMAINDIR="/usr/share/locale"
export TEXTDOMAIN=biglinux-settings

# check current status
check_state() {
  if pacman -Q ollama-rocm &>/dev/null; then
    echo "true"
  else
    echo "false"
  fi
}

info() {
  zenityText=$"Ollama server is running.\nAddress: http://localhost:11434"
  zenity --info --text="$zenityText" --width=300 --height=200
}

# change the state
toggle_state() {
  new_state="$1"
  if [[ "$new_state" == "true" ]];then
    pkexec $PWD/ai/ollamaAmdRun.sh "install" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    info
    exitCode=$?
  else
    pkexec $PWD/ai/ollamaAmdRun.sh "uninstall" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    exitCode=$?
  fi
  exit $exitCode
}

# Executes the function based on the parameter
case "$1" in
    "check")
        check_state
        ;;
    "toggle")
        toggle_state "$2"
        ;;
    "info")
        info
        ;;
    *)
        echo "Use: $0 {check|toggle} [true|false]"
        echo "  check          - Check current status"
        echo "  toggle <state> - Changes to the specified state"
        exit 1
        ;;
esac
