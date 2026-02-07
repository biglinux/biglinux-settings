#!/bin/bash

# check current status
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
elif [ "$1" == "toggle" ]; then
  state="$2"
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    if [ "$state" == "true" ]; then
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
  #   if [ "$state" == "true" ]; then
  #       some command
  #       exitCode=$?
  #   else
  #       some command
  #       exitCode=$?
  #   fi
  # elif [[ "$XDG_CURRENT_DESKTOP" == *"XFCE"* ]];then
  #   if [ "$state" == "true" ]; then
  #       some command
  #       exitCode=$?
  #   else
  #       some command
  #       exitCode=$?
  #   fi
  # elif [[ "$XDG_CURRENT_DESKTOP" == *"Cinnamon"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"X-Cinnamon"* ]];then
  #   if [ "$state" == "true" ]; then
  #       some command
  #       exitCode=$?
  #   else
  #       some command
  #       exitCode=$?
  #   fi
  fi
  exit $exitCode
fi
