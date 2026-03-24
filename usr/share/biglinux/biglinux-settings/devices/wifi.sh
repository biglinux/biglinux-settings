#!/bin/bash

# check current status
# action=$1
if [ "$1" == "check" ];then
  if [[ "$(LANG=C LANGUAGE=C nmcli radio wifi)" == "enabled" ]];then
    echo "true"
  elif [[ "$(LANG=C LANGUAGE=C nmcli radio wifi)" == "disabled" ]];then
    echo "false"
  fi

# change the state
# action=$1
# state=$2
elif [ "$1" == "toggle" ];then
  if [ "$2" == "true" ];then
    nmcli radio wifi on
  else
    nmcli radio wifi off
  fi
  exit $?
fi
