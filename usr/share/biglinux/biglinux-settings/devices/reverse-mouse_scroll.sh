#!/bin/bash

# Config File
kcminputrcFile="$HOME/.config/kcminputrc"

# check current status
check_state() {
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
}

# change the state
toggle_state() {
  new_state="$1"
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    if [[ "$new_state" == "true" ]];then
      kwriteconfig6 --file "$kcminputrcFile" --group "Mouse" --key "NaturalScroll" "true"

      devices=$(qdbus6 org.kde.KWin | grep "/org/kde/KWin/InputDevice/event")
      for device in $devices; do
        qdbus6 org.kde.KWin "$device" org.kde.KWin.InputDevice.naturalScroll true &> /dev/null
      done

      exitCode=$?
    else
      kwriteconfig6 --file "$kcminputrcFile" --group "Mouse" --key "NaturalScroll" "false"

      devices=$(qdbus6 org.kde.KWin | grep "/org/kde/KWin/InputDevice/event")
      for device in $devices; do
        qdbus6 org.kde.KWin "$device" org.kde.KWin.InputDevice.naturalScroll false &> /dev/null
      done

      exitCode=$?
    fi
  # elif [[ "$XDG_CURRENT_DESKTOP" == *"GNOME"* ]];then
  #   if [[ "$new_state" == "true" ]];then
  #       some command
  #       exitCode=$?
  #   else
  #       some command
  #       exitCode=$?
  #   fi
  # elif [[ "$XDG_CURRENT_DESKTOP" == *"XFCE"* ]];then
  #   if [[ "$new_state" == "true" ]];then
  #       some command
  #       exitCode=$?
  #   else
  #       some command
  #       exitCode=$?
  #   fi
  # elif [[ "$XDG_CURRENT_DESKTOP" == *"Cinnamon"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"X-Cinnamon"* ]];then
  #   if [[ "$new_state" == "true" ]];then
  #       some command
  #       exitCode=$?
  #   else
  #       some command
  #       exitCode=$?
  #   fi
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
