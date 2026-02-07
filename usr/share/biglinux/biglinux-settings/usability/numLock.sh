#!/bin/bash

# check current status
if [ "$1" == "check" ]; then
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    if [[ "$(grep Numlock=on /etc/sddm.conf)" ]] || [[ "$(kreadconfig6 --group Keyboard --key "NumLock" --file "$HOME/.config/kcminputrc")" == "0" ]];then
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

# change the state
elif [ "$1" == "toggle" ]; then
  state="$2"
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    if [ "$state" == "true" ]; then
        pkexec kwriteconfig6 --group "General" --key "Numlock" --file "/etc/sddm.conf" "on"
        kwriteconfig6 --group "Keyboard" --key "NumLock" --file "$HOME/.config/kcminputrc" "0"
        exit=$?
    else
        pkexec kwriteconfig6 --group "General" --key "Numlock" --file "/etc/sddm.conf" "off"
        kwriteconfig6 --group "Keyboard" --key "NumLock" --file "$HOME/.config/kcminputrc" "1"
        return $?
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
  fi
  exit $exitCode
fi
