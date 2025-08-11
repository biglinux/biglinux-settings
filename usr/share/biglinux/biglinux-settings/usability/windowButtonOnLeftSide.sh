#!/bin/bash

# check current status
check_state() {
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    if LANG=C grep -q 'FSM' $HOME/.config/kwinrc;then
      echo "true"
    else
      echo "false"
    fi
#   elif [[ "$XDG_CURRENT_DESKTOP" == *"GNOME"* ]];then
#     if [[ "$(LANG=C some Command)" == "true" ]];then #or if some Command &>/dev/null;then # if command response exit 0
#       echo "true"
#     else
#       echo "false"
#     fi
  elif [[ "$XDG_CURRENT_DESKTOP" == *"XFCE"* ]];then
    if [ -n "$(grep SHMC  $HOME/.config/xfce4/xfconf/xfce-perchannel-xml/xfwm4.xml)" ];then
      echo "true"
    else
      echo "false"
    fi
#   elif [[ "$XDG_CURRENT_DESKTOP" == *"Cinnamon"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"X-Cinnamon"* ]];then
#     if [[ "$(LANG=C some Command)" == "true" ]];then #or if some Command &>/dev/null;then # if command response exit 0
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
      kwriteconfig6 --file $HOME/.config/gtk-3.0/settings.ini --group Settings --key "gtk-decoration-layout" "close,maximize,minimize:menu"
      kwriteconfig6 --file $HOME/.config/gtk-4.0/settings.ini --group Settings --key "gtk-decoration-layout" "close,maximize,minimize:menu"
      gsettings set org.gnome.desktop.wm.preferences button-layout "close,maximize,minimize:menu"
      kwriteconfig6 --group "org.kde.kdecoration2" --key "ButtonsOnLeft" --file "$HOME/.config/kwinrc" "XIA"
      kwriteconfig6 --group "org.kde.kdecoration2" --key "ButtonsOnRight" --file "$HOME/.config/kwinrc" "FSM"
      qdbus org.kde.KWin /KWin org.kde.KWin.reconfigure
      exitCode=$?
    else
      kwriteconfig6 --file $HOME/.config/gtk-3.0/settings.ini --group Settings --key "gtk-decoration-layout" "menu:minimize,maximize,close"
      kwriteconfig6 --file $HOME/.config/gtk-4.0/settings.ini --group Settings --key "gtk-decoration-layout" "menu:minimize,maximize,close"
      gsettings set org.gnome.desktop.wm.preferences button-layout "menu:minimize,maximize,close"
      kwriteconfig6 --group "org.kde.kdecoration2" --key "ButtonsOnLeft" --file "$HOME/.config/kwinrc" "MSF"
      kwriteconfig6 --group "org.kde.kdecoration2" --key "ButtonsOnRight" --file "$HOME/.config/kwinrc" "IAX"
      qdbus org.kde.KWin /KWin org.kde.KWin.reconfigure
      exitCode=$?
    fi
#   elif [[ "$XDG_CURRENT_DESKTOP" == *"GNOME"* ]];then
#     if [[ "$new_state" == "true" ]];then
#         some command
#         exitCode=$?
#     else
#         some command
#         exitCode=$?
#     fi
  if [ -n "$(grep SHMC  $HOME/.config/xfce4/xfconf/xfce-perchannel-xml/xfwm4.xml)" ];then
    if [[ "$new_state" == "true" ]];then
        xfconf-query -c xfwm4 -p /general/button_layout -s "CMH|SO"
        exitCode=$?
    else
        xfconf-query -c xfwm4 -p /general/button_layout -s "O|SHMC"
        exitCode=$?
    fi
    export TEXTDOMAINDIR="/usr/share/locale"
    export TEXTDOMAIN=biglinux-settings
    sleep 5 | zenity --progress --title='grub' --text=$"Applying, please wait..." --pulsate --auto-close --no-cancel
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
