#!/bin/bash

#Translation
export TEXTDOMAINDIR="/usr/share/locale"
export TEXTDOMAIN=biglinux-settings

# check current status
check_state() {
  if [[ "kreadconfig6 --file kdeglobals --group KDE --key AnimationDurationFactor" != "0" ]]; then
    echo "false"
  else
    echo "true"
  fi
}

# change the state
toggle_state() {
  new_state="$1"
  if [[ "$new_state" == "true" ]];then
    effects=$(qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.loadedEffects)
    rm $HOME/.config/biglinux-settings/effectsEnable
    for effect in ${effects[@]}; do
      mkdir -p $HOME/.config/biglinux-settings
      echo $effect >> $HOME/.config/biglinux-settingseffectsEnable
      kwriteconfig6 --file kwinrc --group Plugins --key ${effect}Enabled false
      qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.unloadEffect $effect;
    done
    exitCode=$?
  else
    effects=$(cat effectsEnable)
    for effect in ${effects[@]}; do
      kwriteconfig6 --file kwinrc --group Plugins --key ${effect}Enabled true
      qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.loadEffect $effect
    done
    exitCode=$?
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
