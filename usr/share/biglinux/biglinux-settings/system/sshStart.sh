#!/bin/bash

# check current status
if [ "$1" == "check" ]; then
  if [[ "$(systemctl is-active sshd)" == "active" ]];then
    echo "true"
  else
    echo "false"
  fi

# change the state
elif [ "$1" == "toggle" ]; then
  state="$2"
  if [ "$state" == "true" ]; then
      pkexec systemctl start sshd
      exitCode=$?
  else
      pkexec systemctl disable --now sshd
      exitCode=$?
  fi
fi
