#!/bin/bash

dockerComposeAddress="$HOME/Docker/Portainer/docker-compose.yml"

# check current status
# action=$1
if [ "$1" == "check" ]; then
  if [ -n "$(docker compose ls | grep $dockerComposeAddress | grep running)" ]; then
      echo "true"
  else
      echo "false"
  fi

# change the state
# action=$1
# state=$2
elif [ "$1" == "toggle" ]; then
  if [ "$2" == "true" ]; then
    docker compose -f "$dockerComposeAddress" up -d
  else
    docker compose -f "$dockerComposeAddress" down
  fi
  exit $?
fi
