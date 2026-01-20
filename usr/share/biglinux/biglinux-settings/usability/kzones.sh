#!/bin/bash

# check current status
check_state() {
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    if kreadconfig6 --file kwinrc --group Plugins --key kzonesEnabled | grep -q "true"; then
      echo "true"
    else
      echo "false"
    fi
  else
    echo "false"
  fi
}

# change the state
toggle_state() {
  new_state="$1"
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    if [[ "$new_state" == "true" ]];then
        # Check if installed
        if ! pacman -Qi kwin-scripts-kzones &>/dev/null; then
            # Install
            if ! pkexec pacman -S --needed --noconfirm kwin-scripts-kzones; then
                echo "Installation cancelled or failed"
                return 1
            fi
        fi
        
        # Enable
        kwriteconfig6 --file kwinrc --group Plugins --key kzonesEnabled true
        return $?
    else
        # Disable
        kwriteconfig6 --file kwinrc --group Plugins --key kzonesEnabled false
        return $?
    fi
  else
    echo "This feature is only available for KDE Plasma"
    return 1
  fi
}

reload_kwin() {
    if [ "$XDG_SESSION_TYPE" = "wayland" ]; then
        kwin_wayland --replace &
    else
        kwin_x11 --replace &
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
    "reload")
        reload_kwin
        ;;
    *)
        echo "Use: $0 {check|toggle|reload} [true|false]"
        exit 1
        ;;
esac
