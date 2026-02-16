#!/bin/bash

app='chrome'
verifyApp='/opt/google/chrome/chrome'

# check current status
if [ "$1" == "check" ]; then
  if [[ -e "$verifyApp" ]];then
    if [[ -e "/etc/big-preload/enable-${app}" ]];then
      echo "true"
    else
      echo "false"
    fi
  else
    echo ""
  fi

# change the state
elif [ "$1" == "toggle" ]; then
  state="$2"
  if [ "$state" == "true" ]; then
      pkexec touch /etc/big-preload/enable-${app}
      exitCode=$?
  else
      pkexec rm -f /etc/big-preload/enable-${app}
      exitCode=$?
  fi
  exit $exitCode
fi
