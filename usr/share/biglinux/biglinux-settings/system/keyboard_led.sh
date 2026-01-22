#!/bin/bash

# ==============================================================================
# LED Master - Advanced Keyboard LED Control
# ==============================================================================
APP_NAME="LED Master"
CONFIG_FILE="$HOME/.config/led_master.conf"
AUTOSTART_DIR="$HOME/.config/autostart"
AUTOSTART_FILE="$AUTOSTART_DIR/led_master.desktop"
XBINDKEYS_RC="$HOME/.xbindkeysrc"
LED_STATE_FILE="/tmp/led_state_$$"

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

get_config_value() {
    local key="$1"
    if [ -f "$CONFIG_FILE" ]; then
        grep "^${key}=" "$CONFIG_FILE" | cut -d'=' -f2-
    fi
}

set_config_value() {
    local key="$1"
    local value="$2"
    
    mkdir -p "$(dirname "$CONFIG_FILE")"
    
    if [ -f "$CONFIG_FILE" ]; then
        # Remove existing key
        grep -v "^${key}=" "$CONFIG_FILE" > "${CONFIG_FILE}.tmp"
        mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"
    fi
    echo "${key}=${value}" >> "$CONFIG_FILE"
}

# Check if running on X11 or Wayland
get_session_type() {
    echo "${XDG_SESSION_TYPE:-x11}"
}

# ==============================================================================
# DEVICE DETECTION
# ==============================================================================

# Get all LED candidate devices
get_candidates() {
    local session=$(get_session_type)
    local devices=""
    
    # Method 1: brightnessctl (works on both X11 and Wayland)
    if command -v brightnessctl &> /dev/null; then
        devices=$(brightnessctl -l 2>/dev/null | grep -E "input|kbd|scroll|leds" | awk -F"'" '{print $2}' | grep -v "^$")
    fi
    
    # Method 2: xset LED numbers (only X11)
    if [ "$session" = "x11" ]; then
        # Add xset LED options (common ones: 1, 2, 3 for Num/Caps/Scroll Lock)
        for i in 1 2 3 4 5; do
            devices="${devices}"$'\n'"xset:$i"
        done
    fi
    
    echo "$devices" | grep -v "^$" | sort -u
}

# Get method type from device string
get_method_from_device() {
    local device="$1"
    if [[ "$device" == xset:* ]]; then
        echo "xset"
    else
        echo "brightnessctl"
    fi
}

# Get device ID from device string
get_id_from_device() {
    local device="$1"
    if [[ "$device" == xset:* ]]; then
        echo "${device#xset:}"
    else
        echo "$device"
    fi
}

# ==============================================================================
# LED CONTROL
# ==============================================================================

led_on() {
    local method=$(get_config_value "METHOD")
    local device_id=$(get_config_value "ID")
    
    if [ -z "$method" ] || [ -z "$device_id" ]; then
        echo "Error: Not configured" >&2
        return 1
    fi
    
    case "$method" in
        xset)
            xset led "$device_id" 2>/dev/null
            ;;
        brightnessctl)
            brightnessctl --device="$device_id" set 100% 2>/dev/null
            ;;
    esac
    
    # Store state
    echo "on" > "${LED_STATE_FILE}_${device_id}"
}

led_off() {
    local method=$(get_config_value "METHOD")
    local device_id=$(get_config_value "ID")
    
    if [ -z "$method" ] || [ -z "$device_id" ]; then
        return 1
    fi
    
    case "$method" in
        xset)
            xset -led "$device_id" 2>/dev/null
            ;;
        brightnessctl)
            brightnessctl --device="$device_id" set 0 2>/dev/null
            ;;
    esac
    
    # Store state
    rm -f "${LED_STATE_FILE}_${device_id}" 2>/dev/null
}

led_toggle() {
    local method=$(get_config_value "METHOD")
    local device_id=$(get_config_value "ID")
    
    if [ -z "$method" ] || [ -z "$device_id" ]; then
        echo "Error: Not configured" >&2
        return 1
    fi
    
    case "$method" in
        xset)
            if [ "$device_id" = "3" ]; then
                # Scroll Lock - check via xset q
                local state=$(xset q 2>/dev/null | grep "Scroll Lock:" | awk '{print $4}')
                if [ "$state" = "on" ]; then
                    xset -led "$device_id"
                else
                    xset led "$device_id"
                fi
            else
                # Other LEDs - use state file
                local state_file="/tmp/led_xset_state_$device_id"
                if [ -f "$state_file" ]; then
                    xset led "$device_id"
                    rm -f "$state_file"
                else
                    xset -led "$device_id"
                    touch "$state_file"
                fi
            fi
            ;;
        brightnessctl)
            local curr=$(brightnessctl --device="$device_id" get 2>/dev/null)
            if [ "$curr" -gt 0 ] 2>/dev/null; then
                brightnessctl --device="$device_id" set 0
            else
                brightnessctl --device="$device_id" set 100%
            fi
            ;;
    esac
}

# Test a specific device (turn on)
test_device() {
    local device="$1"
    local method=$(get_method_from_device "$device")
    local device_id=$(get_id_from_device "$device")
    
    case "$method" in
        xset)
            xset led "$device_id" 2>/dev/null
            ;;
        brightnessctl)
            brightnessctl --device="$device_id" set 100% 2>/dev/null
            ;;
    esac
}

# Test off a specific device
test_device_off() {
    local device="$1"
    local method=$(get_method_from_device "$device")
    local device_id=$(get_id_from_device "$device")
    
    case "$method" in
        xset)
            xset -led "$device_id" 2>/dev/null
            ;;
        brightnessctl)
            brightnessctl --device="$device_id" set 0 2>/dev/null
            ;;
    esac
}

# ==============================================================================
# CONFIGURATION
# ==============================================================================

save_config() {
    local device="$1"
    local method=$(get_method_from_device "$device")
    local device_id=$(get_id_from_device "$device")
    
    mkdir -p "$(dirname "$CONFIG_FILE")"
    
    cat > "$CONFIG_FILE" << EOF
METHOD=$method
ID=$device_id
EOF
}

is_configured() {
    if [ -f "$CONFIG_FILE" ] && [ -n "$(get_config_value METHOD)" ] && [ -n "$(get_config_value ID)" ]; then
        echo "yes"
    else
        echo "no"
    fi
}

# ==============================================================================
# XMODMAP (X11 only)
# ==============================================================================

apply_xmodmap() {
    if [ "$(get_session_type)" = "x11" ] && command -v xmodmap &> /dev/null; then
        xmodmap -e "add mod3 = Scroll_Lock" 2>/dev/null
    fi
}

get_xmodmap_enabled() {
    get_config_value "USE_XMODMAP"
}

set_xmodmap_enabled() {
    local enabled="$1"
    set_config_value "USE_XMODMAP" "$enabled"
    
    if [ "$enabled" = "true" ]; then
        apply_xmodmap
    fi
}

# ==============================================================================
# XBINDKEYS - HOTKEY
# ==============================================================================

get_hotkey() {
    if [ -f "$XBINDKEYS_RC" ]; then
        # Find our entry and get the key binding
        grep -A1 "led_master" "$XBINDKEYS_RC" 2>/dev/null | tail -1 | sed 's/^[[:space:]]*//'
    fi
}

set_hotkey() {
    local keycode="$1"
    local keyname="$2"
    
    if [ -z "$keycode" ]; then
        return 1
    fi
    
    # Get script path
    local script_path=$(realpath "$0")
    
    # Remove old entry if exists
    if [ -f "$XBINDKEYS_RC" ]; then
        grep -v "led_master" "$XBINDKEYS_RC" | grep -v "^$" > "${XBINDKEYS_RC}.tmp"
        mv "${XBINDKEYS_RC}.tmp" "$XBINDKEYS_RC"
    fi
    
    # Add new entry
    cat >> "$XBINDKEYS_RC" << EOF

# LED Master Toggle
"$script_path led_toggle"
    $keycode
EOF

    # Save to config
    set_config_value "HOTKEY_CODE" "$keycode"
    set_config_value "HOTKEY_NAME" "$keyname"
    
    # Restart xbindkeys
    killall xbindkeys 2>/dev/null
    xbindkeys 2>/dev/null &
}

remove_hotkey() {
    if [ -f "$XBINDKEYS_RC" ]; then
        grep -v "led_master" "$XBINDKEYS_RC" | grep -v "LED Master" > "${XBINDKEYS_RC}.tmp"
        mv "${XBINDKEYS_RC}.tmp" "$XBINDKEYS_RC"
    fi
    
    set_config_value "HOTKEY_CODE" ""
    set_config_value "HOTKEY_NAME" ""
    
    # Restart xbindkeys
    killall xbindkeys 2>/dev/null
    if [ -s "$XBINDKEYS_RC" ]; then
        xbindkeys 2>/dev/null &
    fi
}

get_hotkey_name() {
    get_config_value "HOTKEY_NAME"
}

capture_hotkey() {
    # Capture a key press and return the keycode
    # This uses xbindkeys -k which opens a small window
    if command -v xbindkeys &> /dev/null && [ "$(get_session_type)" = "x11" ]; then
        # Run xbindkeys -k and capture output
        local output=$(timeout 30 xbindkeys -k 2>&1 | grep -v "Press" | grep -v "Release" | grep -v "^$" | head -1)
        echo "$output"
    else
        echo ""
    fi
}

# ==============================================================================
# AUTOSTART
# ==============================================================================

toggle_autostart() {
    local state="$1"
    
    if [ "$state" = "true" ]; then
        # Check if configured
        if [ "$(is_configured)" != "yes" ]; then
            echo "Error: Not configured" >&2
            return 1
        fi
        
        # Enable Autostart
        mkdir -p "$AUTOSTART_DIR"
        local script_path=$(realpath "$0")
        
        cat > "$AUTOSTART_FILE" << EOF
[Desktop Entry]
Type=Application
Exec=$script_path restore
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=LED Master
Comment=Turn on keyboard LED at boot
EOF
        
        # Apply immediately
        led_on
        
        # Apply xmodmap if configured
        if [ "$(get_xmodmap_enabled)" = "true" ]; then
            apply_xmodmap
        fi
        
    else
        # Disable autostart
        rm -f "$AUTOSTART_FILE"
        
        # Turn off LED
        led_off
    fi
}

check_autostart() {
    if [ -f "$AUTOSTART_FILE" ]; then
        echo "true"
    else
        echo "false"
    fi
}

# ==============================================================================
# RESTORE (called by autostart)
# ==============================================================================

restore() {
    # Apply xmodmap if configured
    if [ "$(get_xmodmap_enabled)" = "true" ]; then
        apply_xmodmap
    fi
    
    # Turn on LED
    led_on
    
    # Start xbindkeys if hotkey is configured
    local hotkey=$(get_config_value "HOTKEY_CODE")
    if [ -n "$hotkey" ] && command -v xbindkeys &> /dev/null; then
        xbindkeys 2>/dev/null &
    fi
}

# ==============================================================================
# RESET (remove all configuration)
# ==============================================================================

reset_config() {
    rm -f "$CONFIG_FILE"
    rm -f "$AUTOSTART_FILE"
    remove_hotkey
}

# ==============================================================================
# INFO
# ==============================================================================

get_info() {
    local method=$(get_config_value "METHOD")
    local device_id=$(get_config_value "ID")
    local xmodmap=$(get_xmodmap_enabled)
    local hotkey=$(get_hotkey_name)
    local autostart=$(check_autostart)
    
    cat << EOF
METHOD=$method
ID=$device_id
USE_XMODMAP=$xmodmap
HOTKEY=$hotkey
AUTOSTART=$autostart
SESSION=$(get_session_type)
EOF
}

# ==============================================================================
# MAIN
# ==============================================================================

case "$1" in
    check)
        check_autostart
        ;;
    
    get_candidates)
        get_candidates
        ;;
    
    test)
        test_device "$2"
        ;;
    
    test_off)
        test_device_off "$2"
        ;;
    
    save_config)
        save_config "$2"
        ;;
    
    is_configured)
        is_configured
        ;;
    
    toggle)
        toggle_autostart "$2"
        ;;
    
    led_on)
        led_on
        ;;
    
    led_off)
        led_off
        ;;
    
    led_toggle)
        led_toggle
        ;;
    
    restore)
        restore
        ;;
    
    get_info)
        get_info
        ;;
    
    get_session)
        get_session_type
        ;;
    
    set_xmodmap)
        set_xmodmap_enabled "$2"
        ;;
    
    get_xmodmap)
        get_xmodmap_enabled
        ;;
    
    set_hotkey)
        set_hotkey "$2" "$3"
        ;;
    
    remove_hotkey)
        remove_hotkey
        ;;
    
    get_hotkey)
        get_hotkey_name
        ;;
    
    capture_hotkey)
        capture_hotkey
        ;;
    
    reset)
        reset_config
        ;;
    
    *)
        echo "LED Master - Keyboard LED Control"
        echo ""
        echo "Usage: $0 <command> [args]"
        echo ""
        echo "Commands:"
        echo "  check              - Check if autostart is enabled"
        echo "  get_candidates     - List available LED devices"
        echo "  test <device>      - Test a device (turn on)"
        echo "  test_off <device>  - Test off a device"
        echo "  save_config <dev>  - Save device configuration"
        echo "  is_configured      - Check if configured"
        echo "  toggle <true|false>- Enable/disable autostart"
        echo "  led_on             - Turn LED on"
        echo "  led_off            - Turn LED off"
        echo "  led_toggle         - Toggle LED state"
        echo "  restore            - Restore LED state (for autostart)"
        echo "  get_info           - Get all configuration info"
        echo "  get_session        - Get session type (x11/wayland)"
        echo "  set_xmodmap <bool> - Enable/disable xmodmap fix"
        echo "  get_xmodmap        - Get xmodmap status"
        echo "  set_hotkey <code> <name> - Set toggle hotkey"
        echo "  remove_hotkey      - Remove toggle hotkey"
        echo "  get_hotkey         - Get current hotkey name"
        echo "  capture_hotkey     - Capture a key press"
        echo "  reset              - Remove all configuration"
        ;;
esac
