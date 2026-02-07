#!/bin/bash

# check current status
if [ "$1" == "check" ]; then
  bluetoothState="$(LANG=C LANGUAGE=C timeout 0.1 bluetoothctl show | grep "Powered:" | awk '{print $2}')"
  if [[ "$bluetoothState" == "yes" ]];then
    echo "true"
  elif [[ "$bluetoothState" == "no" ]];then
    echo "false"
  else
    echo "false"
  fi

# change the state
elif [ "$1" == "toggle" ]; then
  state="$2"
  if [ "$state" == "true" ]; then
    timeout 2 bluetoothctl power on
    exitCode=$?
  else
    timeout 2 bluetoothctl power off
    exitCode=$?
  fi
  exit $exitCode
fi
