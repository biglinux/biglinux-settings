#!/bin/bash

# check current status
# action=$1
if [ "$1" == "check" ]; then
  # for KDE Plasma only
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    if [[ "$(LANG=C some Command)" == "true" ]];then #or if some Command &>/dev/null;then # if command response exit 0
      echo "true"
    else
      echo "false"
    fi
  # for GNOME ONly
  elif [[ "$XDG_CURRENT_DESKTOP" == *"GNOME"* ]];then
    if [[ "$(LANG=C some Command)" == "true" ]];then #or if some Command &>/dev/null;then # if command response exit 0
      echo "true"
    else
      echo "false"
    fi
  # for XFCE only
  elif [[ "$XDG_CURRENT_DESKTOP" == *"XFCE"* ]];then
    if [[ "$(LANG=C some Command)" == "true" ]];then #or if some Command &>/dev/null;then # if command response exit 0
      echo "true"
    else
      echo "false"
    fi
  # for CINNAMON only
  elif [[ "$XDG_CURRENT_DESKTOP" == *"Cinnamon"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"X-Cinnamon"* ]];then
    if [[ "$(LANG=C some Command)" == "true" ]];then #or if some Command &>/dev/null;then # if command response exit 0
      echo "true"
    else
      echo "false"
    fi
  fi

# change the state
# action=$1
# state=$2
elif [ "$1" == "toggle" ]; then
  # for KDE Plasma only
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    # if the state is true
    if [ "$2" == "true" ]; then
      # execute a command as a user
      any command as user
      # execute a command as root, prompting for a password only once.
      pkexec $PWD/example/exampleRun.sh "install" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    # if the state is false
    else
      # execute a command as a user
      any command as user
      # execute a command as root, prompting for a password only once.
      pkexec $PWD/example/exampleRun.sh "uninstall" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    fi
  # for GNOME ONly
  elif [[ "$XDG_CURRENT_DESKTOP" == *"GNOME"* ]];then
    # if the state is true
    if [ "$2" == "true" ]; then
      # execute a command as a user
      any command as user
      # execute a command as root, prompting for a password only once.
      pkexec $PWD/example/exampleRun.sh "install" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    # if the state is false
    else
      # execute a command as a user
      any command as user
      # execute a command as root, prompting for a password only once.
      pkexec $PWD/example/exampleRun.sh "uninstall" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    fi
  # for XFCE only
  elif [ -n "$(grep SHMC  $HOME/.config/xfce4/xfconf/xfce-perchannel-xml/xfwm4.xml)" ];then
    # if the state is true
    if [ "$2" == "true" ]; then
      # execute a command as a user
      any command as user
      # execute a command as root, prompting for a password only once.
      pkexec $PWD/example/exampleRun.sh "install" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    # if the state is false
    else
      # execute a command as a user
      any command as user
      # execute a command as root, prompting for a password only once.
      pkexec $PWD/example/exampleRun.sh "uninstall" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    fi
  # for CINNAMON only
  elif [[ "$XDG_CURRENT_DESKTOP" == *"Cinnamon"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"X-Cinnamon"* ]];then
    # if the state is true
    if [ "$2" == "true" ]; then
      # execute a command as a user
      any command as user
      # execute a command as root, prompting for a password only once.
      pkexec $PWD/example/exampleRun.sh "install" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    # if the state is false
    else
      # execute a command as a user
      any command as user
      # execute a command as root, prompting for a password only once.
      pkexec $PWD/example/exampleRun.sh "uninstall" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    fi
  fi
  exit $?
fi
