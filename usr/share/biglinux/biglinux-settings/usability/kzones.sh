#!/bin/bash

# check current status
check_state() {
if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
  if [[ "$(LANG=C kreadconfig6 --file kwinrc --group Plugins --key kzonesEnabled)" == "true" ]];then
    echo "true"
  else
    echo "false"
  fi
fi
}

reload_kwin() {
    if [ "$XDG_SESSION_TYPE" = "wayland" ]; then
        kwin_wayland --replace &
    else
        kwin_x11 --replace &
    fi
}

# change the state
toggle_state() {
  new_state="$1"
  if [[ "$new_state" == "true" ]];then
    if ! pacman -Q kwin-scripts-kzones &>/dev/null; then
      pkexec $PWD/usability/kzonesRun.sh "install" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    fi
    zenityText=$"Kzones will RESTART Plasma, SAVE all programs!!!"
    "zenity --info --text=\"$zenityText\""
    kwriteconfig6 --file kwinrc --group Plugins --key kzonesEnabled true
    reload_kwin
    exitCode=$?
  else
    zenityText=$"Kzones will RESTART Plasma, SAVE all programs!!!"
    "zenity --info --text=\"$zenityText\""
    kwriteconfig6 --file kwinrc --group Plugins --key kzonesEnabled false
    reload_kwin
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
