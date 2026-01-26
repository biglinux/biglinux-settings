#!/bin/bash

# check current status
check_state() {
if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
  if [[ "$(LANG=C jamesdsp --get master_enable)" == "true" ]] && pacman -Q jamesdsp &>/dev/null; then
    echo "true"
  else
    echo "false"
  fi
fi
}

# change the state
toggle_state() {
  new_state="$1"
  if [[ "$new_state" == "true" ]];then
    if ! pacman -Q jamesdsp &>/dev/null; then
      pkexec $PWD/devices/jamesdspRun.sh "install" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    fi
    mkdir -p "$$HOME/.config/jamesdsp/presets"
    cp '/etc/skel/.config/jamesdsp/presets/big-jamesdsp.conf' "$$HOME/.config/jamesdsp/presets/big-jamesdsp.conf"
    jamesdsp --set master_enable=true
    systemctl enable --now --user jamesdsp-autostart.service
    exitCode=$?
  else
    jamesdsp --set master_enable=false
    systemctl disable --now --user jamesdsp-autostart.service
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
    *)
        echo "Use: $0 {check|toggle} [true|false]"
        echo "  check          - Check current status"
        echo "  toggle <state> - Changes to the specified state"
        exit 1
        ;;
esac
