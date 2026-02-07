#!/bin/bash

# check current status
if [ "$1" == "check" ]; then
  # for all DEs
  if [[ "$(LANG=C some Command)" == "true" ]];then #or if some Command &>/dev/null;then # if command response exit 0
    echo "true"
  else
    echo "false"
  fi

# change the state
elif [ "$1" == "toggle" ]; then
  state="$2"
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
  exit $exitCode
fi
