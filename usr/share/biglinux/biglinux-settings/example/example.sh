#!/bin/bash

# check current status
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
elif [ "$1" == "toggle" ]; then
  state="$2"
  # for KDE Plasma only
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    # if the state is true
    if [ "$state" == "true" ]; then
      # execute a command as a user
      any command as user
      # execute a command as root, prompting for a password only once.
      pkexec $PWD/example/exampleRun.sh "install" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
      exitCode=$?
    # if the state is false
    else
      # execute a command as a user
      any command as user
      # execute a command as root, prompting for a password only once.
      pkexec $PWD/example/exampleRun.sh "uninstall" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
      exitCode=$?
    fi
  # for GNOME ONly
  elif [[ "$XDG_CURRENT_DESKTOP" == *"GNOME"* ]];then
    # if the state is true
    if [ "$state" == "true" ]; then
      # execute a command as a user
      any command as user
      # execute a command as root, prompting for a password only once.
      pkexec $PWD/example/exampleRun.sh "install" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
      exitCode=$?
    # if the state is false
    else
      # execute a command as a user
      any command as user
      # execute a command as root, prompting for a password only once.
      pkexec $PWD/example/exampleRun.sh "uninstall" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
      exitCode=$?
    fi
  # for XFCE only
  elif [ -n "$(grep SHMC  $HOME/.config/xfce4/xfconf/xfce-perchannel-xml/xfwm4.xml)" ];then
    # if the state is true
    if [ "$state" == "true" ]; then
      # execute a command as a user
      any command as user
      # execute a command as root, prompting for a password only once.
      pkexec $PWD/example/exampleRun.sh "install" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
      exitCode=$?
    # if the state is false
    else
      # execute a command as a user
      any command as user
      # execute a command as root, prompting for a password only once.
      pkexec $PWD/example/exampleRun.sh "uninstall" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
      exitCode=$?
    fi
  # for CINNAMON only
  elif [[ "$XDG_CURRENT_DESKTOP" == *"Cinnamon"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"X-Cinnamon"* ]];then
    # if the state is true
    if [ "$state" == "true" ]; then
      # execute a command as a user
      any command as user
      # execute a command as root, prompting for a password only once.
      pkexec $PWD/example/exampleRun.sh "install" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
      exitCode=$?
    # if the state is false
    else
      # execute a command as a user
      any command as user
      # execute a command as root, prompting for a password only once.
      pkexec $PWD/example/exampleRun.sh "uninstall" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
      exitCode=$?
    fi
  fi
  exit $exitCode
fi
