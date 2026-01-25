#!/bin/bash
# -----------------------------------------------------------------------------
# Script: biglinux_ultimate_booster.sh
# Description: Advanced Optimization (CPU, GPU, RAM, NETWORK) for BigLinux/Manjaro
# Adapted for GUI Integration
# -----------------------------------------------------------------------------

# Check if running under pkexec/sudo and get real user
if [ "$PKEXEC_UID" ]; then
    CURRENT_USER=$(id -nu "$PKEXEC_UID")
elif [ "$SUDO_USER" ]; then
    CURRENT_USER="$SUDO_USER"
else
    CURRENT_USER=$(logname)
fi

USER_HOME=$(eval echo ~$CURRENT_USER)
USER_ID=$(id -u "$CURRENT_USER")
# Export necessary environment variables for interacting with user session
export XDG_RUNTIME_DIR="/run/user/$USER_ID"
export DBUS_SESSION_BUS_ADDRESS="unix:path=${XDG_RUNTIME_DIR}/bus"

LOG_FILE="/tmp/booster_log.txt"

# Detect proper qdbus binary
QDBUS_CMD="qdbus"
if ! command -v qdbus &>/dev/null; then
    if command -v qdbus-qt5 &>/dev/null; then
        QDBUS_CMD="qdbus-qt5"
    elif command -v qdbus6 &>/dev/null; then
         QDBUS_CMD="qdbus6"
    else
         # Fallback
         QDBUS_CMD="/usr/bin/qdbus" 
    fi
fi

# Detect Baloo (File Indexer)
BALOO_CMD=""
if command -v balooctl6 &>/dev/null; then
    BALOO_CMD="balooctl6"
elif command -v balooctl &>/dev/null; then
    BALOO_CMD="balooctl"
    BALOO_CMD="balooctl"
fi

# Detect Akonadi (PIM Server)
AKONADI_CMD=""
if command -v akonadictl &>/dev/null; then
    AKONADI_CMD="akonadictl"
fi

# Detect kwriteconfig (Plasma 5 vs 6)
if command -v kwriteconfig6 &>/dev/null; then
    K_CONFIG="kwriteconfig6"
    K_READ="kreadconfig6"
elif command -v kwriteconfig5 &>/dev/null; then
    K_CONFIG="kwriteconfig5"
    K_READ="kreadconfig5"
else
    # Fallback or empty if not found
    K_CONFIG="kwriteconfig5"
    K_READ="kreadconfig5"
fi

KWINRC="$USER_HOME/.config/kwinrc"
GLOBALS="$USER_HOME/.config/kdeglobals"

# List of Visual Effects to control
EFFECTS=("wobblywindows" "blur" "backgroundcontrast" "slide" "fadingpopups" "maximize" "minimize" "dialogparent" "dimscreen" "blendchanges" "startupfeedback" "screentransform" "magiclamp" "squash")

# --- Helper Functions ---

log_action() {
    # Strip ANSI codes for clean log/GUI
    CLEAN_MSG=$(echo "$1" | sed 's/\x1b\[[0-9;]*m//g')
    echo "$1" >> $LOG_FILE
    
    if [ "$GUI_MODE" == "1" ]; then
        # In GUI execution, we print a structured status line.
        echo "STATUS:$CLEAN_MSG"
    else
        # In terminal mode, just print the colored message
        echo -e "$1"
    fi
}

progress() {
    if [ "$GUI_MODE" == "1" ]; then
        echo "PROGRESS:$1"
    fi
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        if [ "$GUI_MODE" == "1" ]; then
            echo "STATUS:Error: Must run as root"
        fi
        echo "Root privileges required."
        exit 1
    fi
}

# Helper to check if effect is active
is_effect_active() {
    local status=$(run_as_user $QDBUS_CMD org.kde.KWin /Effects org.kde.kwin.Effects.isEffectLoaded "$1" 2>/dev/null)
    [ "$status" == "true" ]
}

# Helper to check if process is active
is_process_active() {
    pgrep -f "$1" > /dev/null 2>&1
}

# Helper to run command as user
run_as_user() {
    if [ "$EUID" -eq 0 ]; then
        sudo -u "$CURRENT_USER" DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR" "$@"
    else
        "$@"
    fi
}

# --- Optimization Functions ---



gpu_tweaks() {
    MODE=$1
    GPU_VENDOR=$(lspci | grep -i vga | grep -i nvidia > /dev/null && echo "NVIDIA" || echo "AMD")

    if [ "$GPU_VENDOR" == "NVIDIA" ]; then
        if [ "$MODE" == "enable" ]; then
            log_action "[GPU] NVIDIA Detected: Forcing 'Maximum Performance'..."
            # NV settings usually needs X authority too. Trying best effort.
            sudo -u $CURRENT_USER DISPLAY=:0 nvidia-settings -a "[gpu:0]/GpuPowerMizerMode=1" > /dev/null 2>&1
        else
            log_action "[GPU] NVIDIA: Restoring 'Auto' mode..."
            sudo -u $CURRENT_USER DISPLAY=:0 nvidia-settings -a "[gpu:0]/GpuPowerMizerMode=2" > /dev/null 2>&1
        fi
    else
        AMD_PATH="/sys/class/drm/card0/device/power_dpm_force_performance_level"
        if [ -f "$AMD_PATH" ]; then
            if [ "$MODE" == "enable" ]; then
                log_action "[GPU] AMD Detected: Forcing 'high' level..."
                echo "high" > $AMD_PATH
            else
                log_action "[GPU] AMD: Restoring 'auto' level..."
                echo "auto" > $AMD_PATH
            fi
        fi
    fi
}

# --- Main Logic ---


enable_boost() {
    > $LOG_FILE
    check_root
    log_action "Starting Game Mode Booster..."

    # Check and Install GameMode if missing
    if ! command -v gamemoded &> /dev/null; then
        log_action "[SYSTEM] GameMode not found. Installing..."
        progress 5
        # Sync DB to ensure package found, explicit install
        pacman -Sy --noconfirm gamemode lib32-gamemode > /dev/null 2>&1
        if ! command -v gamemoded &> /dev/null; then
             log_action "Error: Failed to install gamemode!"
             exit 1
        fi
        log_action "[SYSTEM] GameMode installed successfully."
    fi

    progress 10

    # Configure GameMode INI for automatic handling
    setup_gamemode_config

    # CPU
    log_action "[CPU] Setting Governor to Performance..."
    # Use generic sysfs method for reliability across distros/tools
    for cpu_gov in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
        echo "performance" > "$cpu_gov" 2>/dev/null
    done
    progress 30

    # RAM


    # KDE/KWin Visual Effects - Direct Control
    log_action "[GPU] Disabling KWin Visual Effects..."
    for effect in "${EFFECTS[@]}"; do
        run_as_user $QDBUS_CMD org.kde.KWin /Effects org.kde.kwin.Effects.unloadEffect "$effect" > /dev/null 2>&1
    done
    progress 50

    # Compositor Settings - Direct kwriteconfig
    log_action "[COMPOSITOR] Applying Performance Settings..."
    run_as_user $K_CONFIG --file kdeglobals --group KDE --key AnimationDurationFactor "0"
    run_as_user $K_CONFIG --file kwinrc --group Plugins --key "kzonesEnabled" "false"
    run_as_user $K_CONFIG --file kwinrc --group Plugins --key "poloniumEnabled" "false"
    run_as_user $K_CONFIG --file kwinrc --group Compositing --key "LatencyPolicy" "Low"
    run_as_user $K_CONFIG --file kwinrc --group Compositing --key "allowTearing" "true"
    
    # Reconfigure KWin
    run_as_user $QDBUS_CMD org.kde.KWin /KWin reconfigure > /dev/null 2>&1
    progress 60

    # Baloo Indexer
    if [ -n "$BALOO_CMD" ]; then
         log_action "[DESKTOP] Suspending and Disabling File Indexer ($BALOO_CMD)..."
         sudo -u $CURRENT_USER DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR" $BALOO_CMD suspend > /dev/null 2>&1
         sudo -u $CURRENT_USER DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR" $BALOO_CMD disable > /dev/null 2>&1
    fi

    # GPU
    gpu_tweaks "enable"
    progress 80


    
    # GameMode Daemon
    log_action "[SYSTEM] Starting GameMode daemon..."
    sudo -u $CURRENT_USER DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR" systemctl --user start gamemoded
    progress 100

    log_action "Optimization Completed!"
}

setup_gamemode_config() {
    # Generate ~/.config/gamemode.ini to ensure KWin effects are disabled
    # whenever GameMode is activated (e.g. by Steam or Lutris)
    
    local CFG_DIR="$USER_HOME/.config"
    local INI_FILE="$CFG_DIR/gamemode.ini"
    
    log_action "[CONFIG] Updating $INI_FILE..."
    
    if [ ! -d "$CFG_DIR" ]; then
        mkdir -p "$CFG_DIR"
        chown "$CURRENT_USER":"$CURRENT_USER" "$CFG_DIR"
    fi

    # Build Start/End Commands
    # We use semicolons to chain commands in gamemode.ini
    
    # 1. Compositor (Removed as per system default)
    GM_START=""
    GM_END=""
    
    # 2. Baloo
    if [ -n "$BALOO_CMD" ]; then
        GM_START="${BALOO_CMD} suspend"
        GM_END="${BALOO_CMD} resume"
    fi

    # Write config
    cat > "$INI_FILE" <<EOF
[general]
desiredgov=performance
igpu_desiredgov=performance
softrealtime=auto
renice=10
ioprio=0

[custom]
start=${GM_START}
end=${GM_END}
EOF

    # Ensure ownership
    chown "$CURRENT_USER":"$CURRENT_USER" "$INI_FILE"
}

disable_boost() {
    > $LOG_FILE
    check_root
    log_action "Reverting to Desktop Mode..."
    progress 10

    # CPU
    log_action "[CPU] Restoring Governor..."
    # Try schedutil first, then ondemand, then powersave as fallback
    FOUND_GOV="ondemand"
    if grep -q "schedutil" /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors 2>/dev/null; then
        FOUND_GOV="schedutil"
    fi
    
    for cpu_gov in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
        echo "$FOUND_GOV" > "$cpu_gov" 2>/dev/null
    done
    progress 30



    # KDE/KWin Visual Effects - Restore
    log_action "[GPU] Restoring KWin Visual Effects..."
    for effect in "${EFFECTS[@]}"; do
        run_as_user $QDBUS_CMD org.kde.KWin /Effects org.kde.kwin.Effects.loadEffect "$effect" > /dev/null 2>&1
    done
    progress 50

    # Compositor Settings - Restore Defaults
    log_action "[COMPOSITOR] Restoring Desktop Settings..."
    run_as_user $K_CONFIG --file kdeglobals --group KDE --key AnimationDurationFactor ""
    run_as_user $K_CONFIG --file kwinrc --group Plugins --key "kzonesEnabled" "true"
    run_as_user $K_CONFIG --file kwinrc --group Compositing --key "LatencyPolicy" "Balance"
    run_as_user $K_CONFIG --file kwinrc --group Compositing --key "allowTearing" "false"
    
    # Reconfigure KWin
    run_as_user $QDBUS_CMD org.kde.KWin /KWin reconfigure > /dev/null 2>&1
    run_as_user $QDBUS_CMD org.kde.KWin /Compositor resume > /dev/null 2>&1
    progress 60
    
    # Baloo
    if [ -n "$BALOO_CMD" ]; then
         log_action "[DESKTOP] Resuming File Indexer..."
         run_as_user $BALOO_CMD enable > /dev/null 2>&1
         run_as_user $BALOO_CMD resume > /dev/null 2>&1
    fi
    
    progress 70

    # Stop GameMode Daemon
    log_action "[SYSTEM] Stopping GameMode daemon..."
    run_as_user systemctl --user stop gamemoded > /dev/null 2>&1
    # Check if we should disable it too (optional, but requested)
    # run_as_user systemctl --user disable gamemoded > /dev/null 2>&1

    # GPU & Network
    gpu_tweaks "disable"
    progress 80


    log_action "System Restored."
    progress 100
}

check_status() {
    # STRICT CHECK: Only consider active if our specific KDE optimizations are applied.
    # We use AnimationDurationFactor=0 as the "signature" of our Game Mode.
    
    if [ -n "$K_READ" ]; then
        ANIM_FACTOR=$(run_as_user $K_READ --file kdeglobals --group KDE --key AnimationDurationFactor 2>/dev/null)
        if [ "$ANIM_FACTOR" == "0" ]; then
            echo "true"
        else
            # If we are in KDE and animation is NOT 0, then our mode is NOT active.
            # Even if CPU is high, it's not "Game Mode Booster" managing it.
            echo "false"
        fi
        return
    fi
    
    # Fallback for non-KDE (if ever used there): Check GameMode daemon status
    if systemctl --user is-active gamemoded --quiet; then
         echo "true"
    else
         echo "false"
    fi
}

generate_report_gui() {
    echo "========================================"
    echo "       SYSTEM STATUS REPORT"
    echo "========================================"
    
    GOV=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null)
    echo "CPU Governor: $GOV"




    
    GM_STATUS=$(sudo -u $CURRENT_USER DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR" systemctl --user is-active gamemoded 2>/dev/null)
    echo "GameMode Daemon: $GM_STATUS"
    
    echo "========================================"
}


case "$1" in
    start_gui)
        GUI_MODE=1
        enable_boost
        generate_report_gui
        ;;
    stop_gui)
        GUI_MODE=1
        disable_boost
        generate_report_gui
        ;;
    check)
        check_status
        ;;
    start)
        enable_boost
        ;;
    stop)
        disable_boost
        ;;
    status)
        generate_report_gui
        ;;
    *)
        echo "Usage: $0 {start|stop|check|status|start_gui|stop_gui}"
        exit 1
        ;;
esac
