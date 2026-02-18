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
  elif [[ "$XDG_CURRENT_DESKTOP" == *"Cinnamon"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"X-Cinnamon"* ]];then
    recent_status=$(gsettings get org.cinnamon.desktop.peripherals.keyboard numlock-state)
    if [[ "$recent_status" == "true" ]]; then
      echo "true"
    else
      echo "false"
    fi
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
#     if [[ "$state" == "true" ]];then
#         some command
#         exitCode=$?
#     else
#         some command
#         exitCode=$?
#     fi
#   elif [[ "$XDG_CURRENT_DESKTOP" == *"XFCE"* ]];then
#     if [[ "$state" == "true" ]];then
#         some command
#         exitCode=$?
#     else
#         some command
#         exitCode=$?
#     fi
  elif [[ "$XDG_CURRENT_DESKTOP" == *"Cinnamon"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"X-Cinnamon"* ]];then
    if [[ "$state" == "true" ]];then
        gsettings set org.cinnamon.desktop.peripherals.keyboard numlock-state true
        numlockx on
        exitCode=$?
    else
        gsettings set org.cinnamon.desktop.peripherals.keyboard numlock-state false
        numlockx off 
        exitCode=$?
    fi
  fi
  exit $exitCode
fi
