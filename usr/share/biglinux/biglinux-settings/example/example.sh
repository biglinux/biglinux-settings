#!/bin/bash

# check current status
# action=$1
if [ "$1" == "check" ]; then
  # for all DEs
  if [[ "$(LANG=C some Command)" == "true" ]];then #or if some Command &>/dev/null;then # if command response exit 0
    echo "true"
  else
    echo "false"
  fi

# change the state
# action=$1
# state=$2
elif [ "$1" == "toggle" ]; then
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
  return=$?
fi
