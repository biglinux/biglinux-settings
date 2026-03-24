#!/bin/bash

# check current status
# action=$1
if [ "$1" == "check" ]; then
  if [[ "$(LANG=C jamesdsp --get master_enable)" == "true" ]] && pacman -Q jamesdsp &>/dev/null; then
    echo "true"
  else
    echo "false"
  fi

# change the state
# action=$1
# state=$2
elif [ "$1" == "toggle" ]; then
  if [ "$2" == "true" ]; then
    if ! pacman -Q jamesdsp &>/dev/null; then
      pkexec $PWD/devices/jamesdspRun.sh "install" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    fi
    mkdir -p "$$HOME/.config/jamesdsp/presets"
    cp '/etc/skel/.config/jamesdsp/presets/big-jamesdsp.conf' "$$HOME/.config/jamesdsp/presets/big-jamesdsp.conf"
    jamesdsp --set master_enable=true
    systemctl enable --now --user jamesdsp-autostart.service
  else
    jamesdsp --set master_enable=false
    systemctl disable --now --user jamesdsp-autostart.service
  fi
  exit $?
fi
