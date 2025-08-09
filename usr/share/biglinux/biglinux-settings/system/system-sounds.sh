#!/bin/bash

check_state() {
    local sounds_enabled=$(gsettings get org.gnome.desktop.sound event-sounds 2>/dev/null)

    if [[ "$sounds_enabled" == "true" ]]; then
        echo "true"
        return 0
    else
        echo "false"
        return 1
    fi
}

toggle_state() {
    local new_state="$1"

    if [[ "$new_state" == "true" ]]; then
        echo "Ativando sons do sistema..."
        gsettings set org.gnome.desktop.sound event-sounds true
        return 0
    else
        echo "Desativando sons do sistema..."
        gsettings set org.gnome.desktop.sound event-sounds false
        return 0
    fi
}

case "$1" in
    "check") check_state ;;
    "toggle") toggle_state "$2" ;;
    *)
        echo "Uso: $0 {check|toggle} [true|false]"
        exit 1
        ;;
esac
