#!/bin/bash

# check current status
if [ "$1" == "check" ]; then
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    if [[ "$(grep Numlock=on /etc/sddm.conf)" ]] || [[ "$(kreadconfig6 --group Keyboard --key "NumLock" --file "$HOME/.config/kcminputrc")" == "0" ]];then
      echo "true"
    else
      echo "false"
    fi
  elif [[ "$XDG_CURRENT_DESKTOP" == *"GNOME"* ]];then
    numlock_state=$(gsettings get org.gnome.desktop.peripherals.keyboard numlock-state 2>/dev/null)
    if [[ "$numlock_state" == "true" ]]; then
      echo "true"
    else
      echo "false"
    fi
  elif [[ "$XDG_CURRENT_DESKTOP" == *"XFCE"* ]];then
    if [ -f "$HOME/.config/autostart/numlockx.desktop" ] && ! grep -q "Hidden=true" "$HOME/.config/autostart/numlockx.desktop" 2>/dev/null; then
      echo "true"
    else
      echo "false"
    fi
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
  elif [[ "$XDG_CURRENT_DESKTOP" == *"GNOME"* ]];then
    if [[ "$state" == "true" ]];then
        gsettings set org.gnome.desktop.peripherals.keyboard remember-numlock-state true 2>/dev/null
        gsettings set org.gnome.desktop.peripherals.keyboard numlock-state true 2>/dev/null
        numlockx on 2>/dev/null
        exitCode=$?
    else
        gsettings set org.gnome.desktop.peripherals.keyboard numlock-state false 2>/dev/null
        numlockx off 2>/dev/null
        exitCode=$?
    fi
  elif [[ "$XDG_CURRENT_DESKTOP" == *"XFCE"* ]];then
    if [[ "$state" == "true" ]];then
        mkdir -p "$HOME/.config/autostart"
        cat > "$HOME/.config/autostart/numlockx.desktop" << 'EOF'
[Desktop Entry]
Type=Application
Name=NumLock On
Exec=numlockx on
NoDisplay=true
X-XFCE-Autostart-Override=true
EOF
        numlockx on 2>/dev/null
        exitCode=$?
    else
        rm -f "$HOME/.config/autostart/numlockx.desktop"
        numlockx off 2>/dev/null
        exitCode=$?
    fi
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
