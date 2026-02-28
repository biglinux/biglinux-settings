#!/bin/bash

# check current status
# action=$1
if [ "$1" == "check" ]; then
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

# change the state
# action=$1
# state=$2
elif [ "$1" == "toggle" ]; then
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    if [ "$2" == "true" ]; then
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
  #   if [ "$2" == "true" ]; then
  #       some command
  #       exitCode=$?
  #   else
  #       some command
  #       exitCode=$?
  #   fi
  # elif [[ "$XDG_CURRENT_DESKTOP" == *"XFCE"* ]];then
  #   if [ "$2" == "true" ]; then
  #       some command
  #       exitCode=$?
  #   else
  #       some command
  #       exitCode=$?
  #   fi
  # elif [[ "$XDG_CURRENT_DESKTOP" == *"Cinnamon"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"X-Cinnamon"* ]];then
  #   if [ "$2" == "true" ]; then
  #       some command
  #       exitCode=$?
  #   else
  #       some command
  #       exitCode=$?
  #   fi
  fi
  exit $exitCode
fi
