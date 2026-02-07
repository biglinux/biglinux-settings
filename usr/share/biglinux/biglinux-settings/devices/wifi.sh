#!/bin/bash

# check current status
if [ "$1" == "check" ];then
  if [[ "$(LANG=C LANGUAGE=C nmcli radio wifi)" == "enabled" ]];then
    echo "true"
  elif [[ "$(LANG=C LANGUAGE=C nmcli radio wifi)" == "disabled" ]];then
    echo "false"
  fi

# change the state
elif [ "$1" == "toggle" ];then
  state="$2"
  if [ "$state" == "true" ];then
    nmcli radio wifi on
    exitCode=$?
  else
    nmcli radio wifi off
    exitCode=$?
  fi
  exit $exitCode
fi
