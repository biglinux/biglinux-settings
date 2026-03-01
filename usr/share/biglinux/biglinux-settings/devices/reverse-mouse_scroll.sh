#!/bin/bash

# Config File
kcminputrcFile="$HOME/.config/kcminputrc"

# check current status
# action=$1
if [ "$1" == "check" ]; then
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    if [[ "$(LANG=C LANGUAGE=C kreadconfig6 --file "$kcminputrcFile" --group "Mouse" --key "NaturalScroll")" == "true" ]];then
      echo "true"
    else
      echo "false"
    fi
  # elif [[ "$XDG_CURRENT_DESKTOP" == *"GNOME"* ]];then
  #   if [[ "$someTest" == "true" ]];then
  #     echo "true"
  #   else
  #     echo "false"
  #   fi
  # elif [[ "$XDG_CURRENT_DESKTOP" == *"XFCE"* ]];then
  #   if [[ "$someTest" == "true" ]];then
  #     echo "true"
  #   else
  #     echo "false"
  #   fi
  # elif [[ "$XDG_CURRENT_DESKTOP" == *"Cinnamon"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"X-Cinnamon"* ]];then
  #   if [[ "$someTest" == "true" ]];then
  #     echo "true"
  #   else
  #     echo "false"
  #   fi
  fi

# change the state
# action=$1
# state=$2
elif [ "$1" == "toggle" ]; then
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    if [ "$2" == "true" ]; then
      kwriteconfig6 --file "$kcminputrcFile" --group "Mouse" --key "NaturalScroll" "true"

      devices=$(qdbus6 org.kde.KWin | grep "/org/kde/KWin/InputDevice/event")
      for device in $devices; do
        qdbus6 org.kde.KWin "$device" org.kde.KWin.InputDevice.naturalScroll true &> /dev/null
      done
    else
      kwriteconfig6 --file "$kcminputrcFile" --group "Mouse" --key "NaturalScroll" "false"

      devices=$(qdbus6 org.kde.KWin | grep "/org/kde/KWin/InputDevice/event")
      for device in $devices; do
        qdbus6 org.kde.KWin "$device" org.kde.KWin.InputDevice.naturalScroll false &> /dev/null
      done
    fi
  # elif [[ "$XDG_CURRENT_DESKTOP" == *"GNOME"* ]];then
  #   if [ "$2" == "true" ]; then
  #       some command
  #   else
  #       some command
  #   fi
  # elif [[ "$XDG_CURRENT_DESKTOP" == *"XFCE"* ]];then
  #   if [ "$2" == "true" ]; then
  #       some command
  #   else
  #       some command
  #   fi
  # elif [[ "$XDG_CURRENT_DESKTOP" == *"Cinnamon"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"X-Cinnamon"* ]];then
  #   if [ "$2" == "true" ]; then
  #       some command
  #   else
  #       some command
  #   fi
  fi
  exit $?
fi
