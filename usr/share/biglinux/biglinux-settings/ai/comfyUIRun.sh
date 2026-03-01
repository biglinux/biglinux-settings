#!/bin/bash

# check current status
# action=$1
if [ "$1" == "check" ]; then
  if [ -n "$(ps aux | grep -i "$HOME/ComfyUI/bin/python $HOME/ComfyUI/main.py" | grep -v grep)" ]; then
    echo "true"
  else
    echo "false"
  fi

# change the state
# action=$1
# state=$2
elif [ "$1" == "toggle" ]; then
  if [ "$2" == "true" ]; then
    $HOME/ComfyUI/bin/python $HOME/ComfyUI/main.py --listen 0.0.0.0 > $HOME/ComfyUI/start.log 2>&1 &
    sleep 5
  else
    kill $(ps aux | grep -i "$HOME/ComfyUI/bin/python $HOME/ComfyUI/main.py" | grep -v grep | awk '{print $2}')
  fi
  exit $?
fi
