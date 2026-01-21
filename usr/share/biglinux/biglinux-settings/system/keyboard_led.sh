#!/bin/bash

# Configuration
CONFIG_FILE="$HOME/.config/meu_led_teclado.conf"
AUTOSTART_DIR="$HOME/.config/autostart"
AUTOSTART_FILE="$AUTOSTART_DIR/teclado_led.desktop"

# Helper to get device from config
get_device() {
    if [ -f "$CONFIG_FILE" ]; then
        grep "DEVICE=" "$CONFIG_FILE" | cut -d'=' -f2
    fi
}

case "$1" in
    check)
        # Check if enabled (Autostart file exists)
        if [ -f "$AUTOSTART_FILE" ]; then
            echo "true"
        else
            echo "false"
        fi
        ;;
    
    get_candidates)
        # List devices for Python to parse
        brightnessctl -l | grep -E "input|kbd|scroll|leds" | awk -F"'" '{print $2}'
        ;;
        
    test)
        # $2 = device name
        DEV="$2"
        if [ -n "$DEV" ]; then
             brightnessctl --device="$DEV" set 100%
        fi
        ;;
        
    test_off)
        # $2 = device name
        DEV="$2"
        if [ -n "$DEV" ]; then
             brightnessctl --device="$DEV" set 0
        fi
        ;;
        
    save_config)
        # $2 = device name
        DEV="$2"
        if [ -n "$DEV" ]; then
            echo "DEVICE=$DEV" > "$CONFIG_FILE"
        fi
        ;;

    toggle)
        STATE="$2" # true or false
        if [ "$STATE" == "true" ]; then
            # Check if configured
            DEV=$(get_device)
            if [ -z "$DEV" ]; then
                echo "Error: Not configured" >&2
                exit 1
            fi

            # Enable Autostart
            mkdir -p "$AUTOSTART_DIR"
            SCRIPT_PATH=$(realpath "$0")
            
            cat > "$AUTOSTART_FILE" <<EOF
[Desktop Entry]
Type=Application
Exec=$SCRIPT_PATH restore
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Keyboard LED On
Comment=Turn on keyboard LED at boot
EOF
            
            # Apply immediately
            brightnessctl --device="$DEV" set 100%
            
        else
            # Disable autostart
            rm -f "$AUTOSTART_FILE"
            
            # Turn Off immediately
            DEV=$(get_device)
            if [ -n "$DEV" ]; then
                brightnessctl --device="$DEV" set 0
            fi
        fi
        ;;
        
    restore)
        # Called by Autostart
        DEV=$(get_device)
        if [ -n "$DEV" ]; then
            brightnessctl --device="$DEV" set 100%
        fi
        ;;
        
    is_configured)
        if [ -f "$CONFIG_FILE" ]; then
            echo "yes"
        else
            echo "no"
        fi
        ;;
esac
