#!/bin/bash

# check current status
if [ "$1" == "check" ]; then
  if [[ "$(powerprofilesctl get)" == "performance" ]];then
    echo "true"
  else
    echo "false"
  fi

# change the state
elif [ "$1" == "toggle" ]; then
  state="$2"
  if [ "$state" == "true" ]; then
    powerprofilesctl set performance
    exitCode=$?
  else
    powerprofilesctl set balanced
    exitCode=$?
  fi
  exit $exitCode
fi
