#!/bin/bash

dockerComposeAddress="$HOME/Docker/Portainer/docker-compose.yml"

# check current status
if [ "$1" == "check" ]; then
  if [ -n "$(docker compose ls | grep $dockerComposeAddress | grep running)" ]; then
      echo "true"
  else
      echo "false"
  fi

# change the state
elif [ "$1" == "toggle" ]; then
  state="$2"
  if [ "$state" == "true" ]; then
    docker compose -f "$dockerComposeAddress" up -d
    exit $exitCode
  else
    docker compose -f "$dockerComposeAddress" down
    exit $exitCode
  fi
  exit $?
fi
