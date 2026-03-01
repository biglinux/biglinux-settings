#!/bin/bash

# check current status
# action=$1
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
# action=$1
# state=$2
elif [ "$1" == "toggle" ]; then
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    if [ "$2" == "true" ]; then
        pkexec kwriteconfig6 --group "General" --key "Numlock" --file "/etc/sddm.conf" "on"
        kwriteconfig6 --group "Keyboard" --key "NumLock" --file "$HOME/.config/kcminputrc" "0"
    else
        pkexec kwriteconfig6 --group "General" --key "Numlock" --file "/etc/sddm.conf" "off"
        kwriteconfig6 --group "Keyboard" --key "NumLock" --file "$HOME/.config/kcminputrc" "1"
    fi
#   elif [[ "$XDG_CURRENT_DESKTOP" == *"GNOME"* ]];then
#     if [[ "$2" == "true" ]];then
#         some command
#     else
#         some command
#     fi
#   elif [[ "$XDG_CURRENT_DESKTOP" == *"XFCE"* ]];then
#     if [[ "$2" == "true" ]];then
#         some command
#     else
#         some command
#     fi
  elif [[ "$XDG_CURRENT_DESKTOP" == *"Cinnamon"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"X-Cinnamon"* ]];then
    if [[ "$2" == "true" ]];then
        gsettings set org.cinnamon.desktop.peripherals.keyboard numlock-state true
        numlockx on
    else
        gsettings set org.cinnamon.desktop.peripherals.keyboard numlock-state false
        numlockx off 
    fi
  fi
  exit $?
fi
