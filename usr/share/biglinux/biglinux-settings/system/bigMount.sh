#!/bin/bash

# check current status
if [ "$1" == "check" ]; then
  if [[ "$(systemctl is-enabled big-mount)" == "enabled" ]];then
    echo "true"
  else
    echo "false"
  fi

# change the state
elif [ "$1" == "toggle" ]; then
  state="$2"
  if [ "$state" == "true" ]; then
      pkexec systemctl enable big-mount
      exitCode=$?
  else
      pkexec systemctl disable big-mount
      exitCode=$?
  fi
  exit $exitCode
fi
