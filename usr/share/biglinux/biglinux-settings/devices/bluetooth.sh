#!/bin/bash

# check current status
# action=$1
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
# action=$1
# state=$2
elif [ "$1" == "toggle" ]; then
  if [ "$2" == "true" ]; then
    timeout 2 bluetoothctl power on
  else
    timeout 2 bluetoothctl power off
  fi
  exit $?
fi
