#!/bin/bash

# check current status
# action=$1
if [ "$1" == "check" ]; then
  if [[ "$(systemctl is-enabled big-mount)" == "enabled" ]];then
    echo "true"
  else
    echo "false"
  fi

# change the state
# action=$1
# state=$2
elif [ "$1" == "toggle" ]; then
  if [ "$2" == "true" ]; then
      pkexec systemctl enable big-mount
  else
      pkexec systemctl disable big-mount
  fi
  exit $?
fi
