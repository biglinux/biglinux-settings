#!/bin/bash
# ==============================================================================
#  KWIN & RAM MASTER CONTROLLER
#  For BigLinux Settings GUI Integration
# ==============================================================================

# --- User Detection for pkexec/sudo ---
if [ "$PKEXEC_UID" ]; then
    CURRENT_USER=$(id -nu "$PKEXEC_UID")
elif [ "$SUDO_USER" ]; then
    CURRENT_USER="$SUDO_USER"
else
    CURRENT_USER=$(logname 2>/dev/null || whoami)
fi

USER_HOME=$(eval echo ~$CURRENT_USER)
USER_ID=$(id -u "$CURRENT_USER")
export XDG_RUNTIME_DIR="/run/user/$USER_ID"
export DBUS_SESSION_BUS_ADDRESS="unix:path=${XDG_RUNTIME_DIR}/bus"

# --- State File ---
STATE_FILE="$USER_HOME/.config/kwin_ram_controller_state.json"
STATE_DIR="$USER_HOME/.config"

# --- Detect QDBUS ---
if command -v qdbus6 &> /dev/null; then 
    QDBUS="qdbus6"
elif command -v qdbus &> /dev/null; then
    QDBUS="qdbus"
else
    QDBUS="/usr/bin/qdbus"
fi

# --- Detect Baloo ---
if command -v balooctl6 &> /dev/null; then 
    BALOO_CMD="balooctl6"
elif command -v balooctl &> /dev/null; then
    BALOO_CMD="balooctl"
else
    BALOO_CMD=""
fi

# --- Detect Akonadi ---
if command -v akonadictl &> /dev/null; then 
    AKONADI_CMD="akonadictl"
else
    AKONADI_CMD=""
fi

# --- Detect kwriteconfig ---
if command -v kwriteconfig6 &> /dev/null; then
    K_CONFIG="kwriteconfig6"
    K_READ="kreadconfig6"
elif command -v kwriteconfig5 &> /dev/null; then
    K_CONFIG="kwriteconfig5"
    K_READ="kreadconfig5"
else
    K_CONFIG=""
    K_READ=""
fi

# --- Visual Effects List ---
EFFECTS="wobblywindows blur backgroundcontrast slide fadingpopups maximize minimize dialogparent dimscreen blendchanges startupfeedback screentransform magiclamp squash"

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

log_status() {
    echo "STATUS:$1"
}

log_progress() {
    echo "PROGRESS:$1"
}

run_as_user() {
    sudo -u "$CURRENT_USER" DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR" "$@"
}

is_effect_active() {
    local status=$(run_as_user $QDBUS org.kde.KWin /Effects org.kde.kwin.Effects.isEffectLoaded "$1" 2>/dev/null)
    [ "$status" == "true" ]
}

is_process_active() {
    pgrep -f "$1" > /dev/null 2>&1
}

# Get current animation factor
get_animation_factor() {
    if [ -n "$K_READ" ]; then
        run_as_user $K_READ --file kdeglobals --group KDE --key AnimationDurationFactor 2>/dev/null
    fi
}

# ==============================================================================
# STATE MANAGEMENT
# ==============================================================================

save_state() {
    mkdir -p "$STATE_DIR"
    
    # Collect current state
    local effects_state=""
    for effect in $EFFECTS; do
        if is_effect_active "$effect"; then
            effects_state="$effects_state\"$effect\":true,"
        else
            effects_state="$effects_state\"$effect\":false,"
        fi
    done
    effects_state="${effects_state%,}"
    
    local baloo_running="false"
    if [ -n "$BALOO_CMD" ] && is_process_active "baloo_file"; then
        baloo_running="true"
    fi
    
    local akonadi_running="false"
    if [ -n "$AKONADI_CMD" ] && is_process_active "akonadi_control"; then
        akonadi_running="true"
    fi
    
    local anim_factor=$(get_animation_factor)
    [ -z "$anim_factor" ] && anim_factor="1"
    
    local latency_policy=""
    local allow_tearing="false"
    local kzones_enabled="true"
    
    if [ -n "$K_READ" ]; then
        latency_policy=$(run_as_user $K_READ --file kwinrc --group Compositing --key LatencyPolicy 2>/dev/null)
        allow_tearing=$(run_as_user $K_READ --file kwinrc --group Compositing --key allowTearing 2>/dev/null)
        kzones_enabled=$(run_as_user $K_READ --file kwinrc --group Plugins --key kzonesEnabled 2>/dev/null)
    fi
    
    [ -z "$latency_policy" ] && latency_policy="Balance"
    [ -z "$allow_tearing" ] && allow_tearing="false"
    [ -z "$kzones_enabled" ] && kzones_enabled="true"
    
    cat > "$STATE_FILE" << EOF
{
    "effects": {$effects_state},
    "baloo_running": $baloo_running,
    "akonadi_running": $akonadi_running,
    "animation_factor": "$anim_factor",
    "latency_policy": "$latency_policy",
    "allow_tearing": "$allow_tearing",
    "kzones_enabled": "$kzones_enabled"
}
EOF
    chown "$CURRENT_USER":"$CURRENT_USER" "$STATE_FILE"
}

# ==============================================================================
# INDIVIDUAL CONTROL FUNCTIONS
# ==============================================================================

# --- GPU Effects Control ---
control_effects() {
    local action=$1  # "off" or "on"
    
    for effect in $EFFECTS; do
        if [ "$action" == "off" ]; then
            run_as_user $QDBUS org.kde.KWin /Effects org.kde.kwin.Effects.unloadEffect "$effect" > /dev/null 2>&1
        else
            run_as_user $QDBUS org.kde.KWin /Effects org.kde.kwin.Effects.loadEffect "$effect" > /dev/null 2>&1
        fi
    done
}

# --- Akonadi Control ---
control_akonadi() {
    local action=$1  # "stop" or "start"
    
    if [ -z "$AKONADI_CMD" ]; then
        echo "NOT_INSTALLED"
        return
    fi
    
    if [ "$action" == "stop" ]; then
        run_as_user $AKONADI_CMD stop > /dev/null 2>&1
    else
        run_as_user $AKONADI_CMD start > /dev/null 2>&1
    fi
}

# --- Baloo Control ---
control_baloo() {
    local action=$1  # "suspend" or "resume"
    
    if [ -z "$BALOO_CMD" ]; then
        echo "NOT_INSTALLED"
        return
    fi
    
    if [ "$action" == "suspend" ]; then
        run_as_user $BALOO_CMD suspend > /dev/null 2>&1
        pkill baloo_file > /dev/null 2>&1
    else
        run_as_user $BALOO_CMD resume > /dev/null 2>&1
    fi
}

# --- SMART Monitor Control ---
control_smart() {
    local action=$1  # "unload" or "load"
    
    if [ "$action" == "unload" ]; then
        run_as_user $QDBUS org.kde.kded6 /kded org.kde.kded6.unloadModule "smart" > /dev/null 2>&1
    else
        run_as_user $QDBUS org.kde.kded6 /kded org.kde.kded6.loadModule "smart" > /dev/null 2>&1
    fi
}

# --- Cache Cleaning ---
clean_cache() {
    sync
    echo 3 > /proc/sys/vm/drop_caches 2>/dev/null
}

# --- Compositor Settings ---
apply_performance_settings() {
    if [ -z "$K_CONFIG" ]; then
        return
    fi
    
    run_as_user $K_CONFIG --file kdeglobals --group KDE --key AnimationDurationFactor "0"
    run_as_user $K_CONFIG --file kwinrc --group Plugins --key "kzonesEnabled" "false"
    run_as_user $K_CONFIG --file kwinrc --group Plugins --key "poloniumEnabled" "false"
    run_as_user $K_CONFIG --file kwinrc --group Compositing --key "LatencyPolicy" "Low"
    run_as_user $K_CONFIG --file kwinrc --group Compositing --key "allowTearing" "true"
    
    run_as_user $QDBUS org.kde.KWin /KWin reconfigure > /dev/null 2>&1
}

restore_desktop_settings() {
    if [ -z "$K_CONFIG" ]; then
        return
    fi
    
    # Read from state file if exists
    local anim_factor="1"
    local latency_policy="Balance"
    local allow_tearing="false"
    local kzones_enabled="true"
    
    if [ -f "$STATE_FILE" ]; then
        anim_factor=$(grep -o '"animation_factor": *"[^"]*"' "$STATE_FILE" | cut -d'"' -f4)
        latency_policy=$(grep -o '"latency_policy": *"[^"]*"' "$STATE_FILE" | cut -d'"' -f4)
        allow_tearing=$(grep -o '"allow_tearing": *"[^"]*"' "$STATE_FILE" | cut -d'"' -f4)
        kzones_enabled=$(grep -o '"kzones_enabled": *"[^"]*"' "$STATE_FILE" | cut -d'"' -f4)
    fi
    
    [ -z "$anim_factor" ] || [ "$anim_factor" == "0" ] && anim_factor="1"
    [ -z "$latency_policy" ] && latency_policy="Balance"
    [ -z "$allow_tearing" ] && allow_tearing="false"
    [ -z "$kzones_enabled" ] && kzones_enabled="true"
    
    run_as_user $K_CONFIG --file kdeglobals --group KDE --key AnimationDurationFactor "$anim_factor"
    run_as_user $K_CONFIG --file kwinrc --group Plugins --key "kzonesEnabled" "$kzones_enabled"
    run_as_user $K_CONFIG --file kwinrc --group Compositing --key "LatencyPolicy" "$latency_policy"
    run_as_user $K_CONFIG --file kwinrc --group Compositing --key "allowTearing" "$allow_tearing"
    
    run_as_user $QDBUS org.kde.KWin /KWin reconfigure > /dev/null 2>&1
}

# ==============================================================================
# MAIN ACTIONS
# ==============================================================================

enable_performance() {
    log_status "Saving current state..."
    save_state
    log_progress 10
    
    log_status "Disabling GPU Effects..."
    control_effects "off"
    log_progress 30
    
    log_status "Stopping Akonadi Server..."
    control_akonadi "stop"
    log_progress 40
    
    log_status "Suspending Baloo Indexer..."
    control_baloo "suspend"
    log_progress 50
    
    log_status "Unloading SMART Monitor..."
    control_smart "unload"
    log_progress 60
    
    log_status "Cleaning RAM Cache..."
    clean_cache
    log_progress 80
    
    log_status "Applying Performance Settings..."
    apply_performance_settings
    log_progress 100
    
    log_status "Performance Mode Enabled!"
    
    run_as_user notify-send "🚀 MODO GAMING" "RAM limpa e Efeitos desligados" -i input-gaming 2>/dev/null
}

restore_desktop() {
    log_status "Restoring GPU Effects..."
    control_effects "on"
    log_progress 25
    
    log_status "Resuming Baloo Indexer..."
    control_baloo "resume"
    log_progress 50
    
    log_status "Loading SMART Monitor..."
    control_smart "load"
    log_progress 75
    
    log_status "Restoring Desktop Settings..."
    restore_desktop_settings
    log_progress 100
    
    log_status "Desktop Mode Restored!"
    
    run_as_user notify-send "🍃 MODO DESKTOP" "Sistema restaurado" -i video-display 2>/dev/null
}

# --- Individual toggles for GUI ---
toggle_effects() {
    local state=$1  # "true" = enabled (load), "false" = disabled (unload)
    if [ "$state" == "true" ]; then
        control_effects "on"
    else
        control_effects "off"
    fi
}

toggle_akonadi() {
    local state=$1
    if [ "$state" == "true" ]; then
        control_akonadi "start"
    else
        control_akonadi "stop"
    fi
}

toggle_baloo() {
    local state=$1
    if [ "$state" == "true" ]; then
        control_baloo "resume"
    else
        control_baloo "suspend"
    fi
}

toggle_smart() {
    local state=$1
    if [ "$state" == "true" ]; then
        control_smart "load"
    else
        control_smart "unload"
    fi
}

toggle_compositor_settings() {
    local state=$1
    if [ "$state" == "true" ]; then
        restore_desktop_settings
    else
        apply_performance_settings
    fi
}

# --- Check current overall status ---
check_status() {
    local anim_factor=$(get_animation_factor)
    if [ "$anim_factor" == "0" ]; then
        echo "true"  # Performance mode active
    else
        echo "false"  # Desktop mode
    fi
}

# --- Get status for individual items ---
get_effects_status() {
    # Check first effect as indicator
    if is_effect_active "blur"; then
        echo "true"
    else
        echo "false"
    fi
}

get_akonadi_status() {
    if [ -z "$AKONADI_CMD" ]; then
        echo "NOT_INSTALLED"
    elif is_process_active "akonadi_control"; then
        echo "true"
    else
        echo "false"
    fi
}

get_baloo_status() {
    if [ -z "$BALOO_CMD" ]; then
        echo "NOT_INSTALLED"
    elif is_process_active "baloo_file"; then
        echo "true"
    else
        echo "false"
    fi
}

get_compositor_status() {
    local anim_factor=$(get_animation_factor)
    if [ "$anim_factor" == "0" ]; then
        echo "false"  # Performance mode (desktop settings off)
    else
        echo "true"   # Normal mode
    fi
}

# ==============================================================================
# MAIN SWITCH
# ==============================================================================

case "$1" in
    enable_gui)
        enable_performance
        ;;
    disable_gui)
        restore_desktop
        ;;
    check)
        check_status
        ;;
    toggle_effects)
        toggle_effects "$2"
        ;;
    toggle_akonadi)
        toggle_akonadi "$2"
        ;;
    toggle_baloo)
        toggle_baloo "$2"
        ;;
    toggle_smart)
        toggle_smart "$2"
        ;;
    toggle_compositor)
        toggle_compositor_settings "$2"
        ;;
    clean_cache)
        clean_cache
        echo "OK"
        ;;
    get_effects_status)
        get_effects_status
        ;;
    get_akonadi_status)
        get_akonadi_status
        ;;
    get_baloo_status)
        get_baloo_status
        ;;
    get_compositor_status)
        get_compositor_status
        ;;
    save_state)
        save_state
        echo "OK"
        ;;
    *)
        echo "Usage: $0 {enable_gui|disable_gui|check|toggle_*|get_*_status|clean_cache|save_state}"
        exit 1
        ;;
esac
