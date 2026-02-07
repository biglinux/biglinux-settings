#!/bin/bash

# check current status
if [ "$1" == "check" ]; then
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

# change the state
elif [ "$1" == "toggle" ]; then
  state="$2"
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    if [ "$state" == "true" ]; then
      kwriteconfig6 --file $HOME/.config/gtk-3.0/settings.ini --group Settings --key "gtk-decoration-layout" "close,minimize,maximize:menu"
      kwriteconfig6 --file $HOME/.config/gtk-4.0/settings.ini --group Settings --key "gtk-decoration-layout" "close,minimize,maximize:menu"
      gsettings set org.gnome.desktop.wm.preferences button-layout "close,minimize,maximize:menu"
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
#     if [ "$state" == "true" ]; then
#         some command
#         exitCode=$?
#     else
#         some command
#         exitCode=$?
#     fi
  elif [ -n "$(grep SHMC  $HOME/.config/xfce4/xfconf/xfce-perchannel-xml/xfwm4.xml)" ];then
    if [ "$state" == "true" ]; then
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
#     if [ "$state" == "true" ]; then
#         some command
#         exitCode=$?
#     else
#         some command
#         exitCode=$?
#     fi
  fi
  exit $exitCode
fi
