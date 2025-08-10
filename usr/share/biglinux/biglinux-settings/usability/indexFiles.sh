#!/bin/bash

# check current status
check_state() {
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    if LANG=C balooctl6 status &>/dev/null;then
      echo "true"
    else
      echo "false"
    fi
#   elif [[ "$XDG_CURRENT_DESKTOP" == *"GNOME"* ]];then
#     if [[ "$someTest" == "true" ]];then
#       echo "true"
#     else
#       echo "false"
#     fi
#   elif [[ "$XDG_CURRENT_DESKTOP" == *"XFCE"* ]];then
#     if [[ "$someTest" == "true" ]];then
#       echo "true"
#     else
#       echo "false"
#     fi
#   elif [[ "$XDG_CURRENT_DESKTOP" == *"Cinnamon"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"X-Cinnamon"* ]];then
#     if [[ "$someTest" == "true" ]];then
#       echo "true"
#     else
#       echo "false"
#     fi
  fi
}

# change the state
toggle_state() {
  new_state="$1"
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    if [[ "$new_state" == "true" ]];then
        balooctl6 enable &>/dev/null
    else
        balooctl6 disable &>/dev/null
    fi
#   elif [[ "$XDG_CURRENT_DESKTOP" == *"GNOME"* ]];then
#     if [[ "$new_state" == "true" ]];then
#         some command
#         exitCode=$?
#     else
#         some command
#         exitCode=$?
#     fi
#   elif [[ "$XDG_CURRENT_DESKTOP" == *"XFCE"* ]];then
#     if [[ "$new_state" == "true" ]];then
#         some command
#         exitCode=$?
#     else
#         some command
#         exitCode=$?
#     fi
#   elif [[ "$XDG_CURRENT_DESKTOP" == *"Cinnamon"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"X-Cinnamon"* ]];then
#     if [[ "$new_state" == "true" ]];then
#         some command
#         exitCode=$?
#     else
#         some command
#         exitCode=$?
#     fi
    exit $exitCode
  fi
}

# Executes the function based on the parameter
case "$1" in
    "check")
        check_state
        ;;
    "toggle")
        toggle_state "$2"
        ;;
    *)
        echo "Use: $0 {check|toggle} [true|false]"
        echo "  check          - Check current status"
        echo "  toggle <state> - Changes to the specified state"
        exit 1
        ;;
esac
