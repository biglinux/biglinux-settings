#!/bin/bash

# check current status
check_state() {
if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
  if [[ "$(LANG=C kreadconfig6 --file kwinrc --group Plugins --key kzonesEnabled)" == "true" ]] && pacman -Q kwin-scripts-kzones &>/dev/null; then
    echo "true"
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
  else
    echo "false"
  fi
fi
}

# change the state
toggle_state() {
  new_state="$1"
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    if [[ "$new_state" == "true" ]];then
      if ! pacman -Q kwin-scripts-kzones &>/dev/null; then
        pkexec $PWD/usability/kzonesRun.sh "install" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
      fi
      kwriteconfig6 --file kwinrc --group Plugins --key kzonesEnabled true
      qdbus6 org.kde.KWin /KWin reconfigure
      exitCode=$?
    else
      kwriteconfig6 --file kwinrc --group Plugins --key kzonesEnabled false
      qdbus6 org.kde.KWin /KWin reconfigure
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
