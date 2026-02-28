#!/bin/bash

#Translation
export TEXTDOMAINDIR="/usr/share/locale"
export TEXTDOMAIN=biglinux-settings

# check current status
# action=$1
if [ "$1" == "check" ]; then
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    if [[ -n "$(qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.loadedEffects)" ]]; then
      echo "false"
    else
      echo "true"
    fi
  # elif [[ "$XDG_CURRENT_DESKTOP" == *"GNOME"* ]];then
  #   if [[ "$someTest" == "true" ]];then
  #     echo "true"
  #   else
  #     echo "false"
  #   fi
  # elif [[ "$XDG_CURRENT_DESKTOP" == *"XFCE"* ]];then
  #   if [[ "$someTest" == "true" ]];then
  #     echo "true"
  #   else
  #     echo "false"
  #   fi
  # elif [[ "$XDG_CURRENT_DESKTOP" == *"Cinnamon"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"X-Cinnamon"* ]];then
  #   if [[ "$someTest" == "true" ]];then
  #     echo "true"
  #   else
  #     echo "false"
  #   fi
  fi

# change the state
# action=$1
# state=$2
elif [ "$1" == "toggle" ]; then
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    if [ "$2" == "true" ]; then
      effects=$(qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.loadedEffects)
      rm $HOME/.config/biglinux-settings/effectsEnable
      for effect in ${effects[@]}; do
        mkdir -p $HOME/.config/biglinux-settings
        echo $effect >> $HOME/.config/biglinux-settings/effectsEnable
        kwriteconfig6 --file kwinrc --group Plugins --key ${effect}Enabled false
        qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.unloadEffect $effect;
      done
      exitCode=$?
    else
      effects=$(cat $HOME/.config/biglinux-settings/effectsEnable)
      for effect in ${effects[@]}; do
        kwriteconfig6 --file kwinrc --group Plugins --key ${effect}Enabled true
        qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.loadEffect $effect
      done
      exitCode=$?
    fi
  # elif [[ "$XDG_CURRENT_DESKTOP" == *"GNOME"* ]];then
  #   if [ "$2" == "true" ]; then
  #       some command
  #       exitCode=$?
  #   else
  #       some command
  #       exitCode=$?
  #   fi
  # elif [[ "$XDG_CURRENT_DESKTOP" == *"XFCE"* ]];then
  #   if [ "$2" == "true" ]; then
  #       some command
  #       exitCode=$?
  #   else
  #       some command
  #       exitCode=$?
  #   fi
  # elif [[ "$XDG_CURRENT_DESKTOP" == *"Cinnamon"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"X-Cinnamon"* ]];then
  #   if [ "$2" == "true" ]; then
  #       some command
  #       exitCode=$?
  #   else
  #       some command
  #       exitCode=$?
  #   fi
  fi
  exit $exitCode
fi
