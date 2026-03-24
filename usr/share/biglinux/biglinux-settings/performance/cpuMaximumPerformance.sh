#!/bin/bash

# check current status
# action=$1
if [ "$1" == "check" ]; then
  if [[ "$(powerprofilesctl get)" == "performance" ]];then
    echo "true"
  else
    echo "false"
  fi

# change the state
# action=$1
# state=$2
elif [ "$1" == "toggle" ]; then
  if [ "$2" == "true" ]; then
    powerprofilesctl set performance
  else
    powerprofilesctl set balanced
  fi
  exit $?
fi
