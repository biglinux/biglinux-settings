#!/bin/bash

# #Translation
# export TEXTDOMAINDIR="/usr/share/locale"
# export TEXTDOMAIN=biglinux-settings

# # check current status
# check_state() {
#   if [[ "kreadconfig6 --file kwinrc --group Effects --key Active" == "false" ]] && [[ "kreadconfig6 --file kwinrc --group Effects --key Effects" == "0" ]]; then
#     echo "true"
#   else
#     echo "false"
#   fi
# }

# # change the state
# toggle_state() {
#   new_state="$1"
#   if [[ "$new_state" == "true" ]];then
#     kwriteconfig6 --config kwinrc --group Effects --key Active false
#     kwriteconfig6 --config kwinrc --group Effects --key Effects 0
#     exitCode=$?
#   else
#     kwriteconfig6 --config kwinrc --group Effects --key Active true
#     kwriteconfig6 --config kwinrc --group Effects --key Effects 1
#     exitCode=$?
#   fi
#   exit $exitCode
# }

# # Executes the function based on the parameter
# case "$1" in
#     "check")
#         check_state
#         ;;
#     "toggle")
#         toggle_state "$2"
#         ;;
#     *)
#         echo "Use: $0 {check|toggle} [true|false]"
#         echo "  check          - Check current status"
#         echo "  toggle <state> - Changes to the specified state"
#         exit 1
#         ;;
# esac
