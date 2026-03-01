#!/bin/bash

#Translation
export TEXTDOMAINDIR="/usr/share/locale"
export TEXTDOMAIN=biglinux-settings

# check current status
# action=$1
if [ "$1" == "check" ]; then
  if [ -d "$HOME/ComfyUI" ]; then
    echo "true"
  else
    echo "false"
  fi

# change the state
# action=$1
# state=$2
elif [ "$1" == "toggle" ]; then
  if [ "$2" == "true" ]; then
    vgaList=$(lspci | grep -iE "VGA|3D|Display")
    if [[ -z "$(echo $vgaList | grep -Ei '(nvidia|radeon|amd|\bati)')" ]]; then
      zenityText=$"AMD/Nvidia GPU not found!"
      zenity --info --text="$zenityText"
      exit 1
    fi

    # install depends as root
    if ! pacman -Q python-pip &>/dev/null || ! pacman -Q git &>/dev/null; then
      pkexec $PWD/ai/comfyUIDepends.sh "install" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    fi
    # install comfyUI as user
    $PWD/ai/comfyUIInstall.sh "install"
  else
    $PWD/ai/comfyUIInstall.sh "uninstall"
  fi
  exit $?
fi
