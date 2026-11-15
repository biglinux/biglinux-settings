#!/bin/bash

# check current status
# action=$1
if [ "$1" == "check" ]; then
  if [[ -e "$verifyApp" ]];then
    # big-preload always reads the account's default browser, flag or not:
    # its switch would change nothing, so the page leaves it out.
    if [[ -n $desktopId && $(xdg-mime query default x-scheme-handler/https 2>/dev/null) == "$desktopId" ]]; then
      echo "true_disabled"
    elif [[ -e "/etc/big-preload/enable-$app" ]];then
      echo "true"
    else
      echo "false"
    fi
  else
    echo ""
  fi

# change the state
# action=$1
# state=$2
elif [ "$1" == "toggle" ]; then
  if [ "$2" == "true" ]; then
    pkexec touch /etc/big-preload/enable-$app
  else
    pkexec rm -f /etc/big-preload/enable-$app
  fi
  return=$?
fi
