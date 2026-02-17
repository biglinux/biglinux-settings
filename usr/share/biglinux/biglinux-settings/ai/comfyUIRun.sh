#!/bin/bash
# check current status
if [ "$1" == "check" ]; then
  if [ -n "$(ps aux | grep -i "$HOME/ComfyUI/bin/python $HOME/ComfyUI/main.py" | grep -v grep)" ]; then
    echo "true"
  else
    echo "false"
  fi

elif [ "$1" == "toggle" ]; then
  state="$2"
  if [ "$state" == "true" ]; then
    $HOME/ComfyUI/bin/python $HOME/ComfyUI/main.py --listen 0.0.0.0 > $HOME/ComfyUI/start.log 2>&1 &
    sleep 5
    exitCode=$?
  else
    kill $(ps aux | grep -i "$HOME/ComfyUI/bin/python $HOME/ComfyUI/main.py" | grep -v grep | awk '{print $2}')
    exitCode=$?
  fi
  exit $exitCode
fi
