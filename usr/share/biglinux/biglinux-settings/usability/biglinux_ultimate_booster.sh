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

# Detect kwriteconfig (Plasma 5 vs 6)
if command -v kwriteconfig6 &>/dev/null; then
    K_CONFIG="kwriteconfig6"
elif command -v kwriteconfig5 &>/dev/null; then
    K_CONFIG="kwriteconfig5"
else
    # Fallback or empty if not found
    K_CONFIG="kwriteconfig5" 
fi

KWINRC="$USER_HOME/.config/kwinrc"
GLOBALS="$USER_HOME/.config/kdeglobals"

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

# --- Optimization Functions ---

network_tweaks() {
    MODE=$1
    if [ "$MODE" == "enable" ]; then
        log_action "[NETWORK] Enabling TCP BBR and FQ_CODEL (Anti-Lag)..."
        
        modprobe tcp_bbr 2>/dev/null
        sysctl -w net.core.default_qdisc=fq_codel > /dev/null
        sysctl -w net.ipv4.tcp_congestion_control=bbr > /dev/null
        
        WIFI_IFACE=$(iw dev | awk '$1=="Interface"{print $2}')
        if [ ! -z "$WIFI_IFACE" ]; then
            log_action "[NETWORK] Disabling Wi-Fi Power Save ($WIFI_IFACE)..."
            iw dev $WIFI_IFACE set power_save off 2>/dev/null
        fi
        
    else
        log_action "[NETWORK] Restoring network defaults..."
        sysctl -w net.core.default_qdisc=pfifo_fast > /dev/null
        sysctl -w net.ipv4.tcp_congestion_control=cubic > /dev/null
        
        WIFI_IFACE=$(iw dev | awk '$1=="Interface"{print $2}')
        if [ ! -z "$WIFI_IFACE" ]; then
            iw dev $WIFI_IFACE set power_save on 2>/dev/null
        fi
    fi
}

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
    log_action "[RAM] Reducing Swappiness to 10..."
    sysctl -w vm.swappiness=10 > /dev/null
    progress 50

    # DEEP KDE OPTIMIZATION (Via Python Helper)
    SCRIPT_DIR=$(dirname "$0")
    PYTHON_HELPER="$SCRIPT_DIR/kde_booster.py"
    
    if [ -f "$PYTHON_HELPER" ]; then
        log_action "[PLASMA] Running advanced KDE optimization..."
        # Run as user, as these are user configs
        sudo -u $CURRENT_USER python3 "$PYTHON_HELPER" on
    fi

    # Compositor & Reload (Legacy Fallback / Double Check)
    if pgrep -x "kwin_x11" > /dev/null || pgrep -x "kwin_wayland" > /dev/null; then
        log_action "[DESKTOP] Reloading KWin to apply changes..."
        # Reconfigure call to apply kwriteconfig changes immediately
        sudo -u $CURRENT_USER DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR" $QDBUS_CMD org.kde.KWin /KWin reconfigure > /dev/null 2>&1
        # Explicit suspend call just in case
        sudo -u $CURRENT_USER DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR" $QDBUS_CMD org.kde.KWin /Compositor suspend > /dev/null 2>&1
    fi
    progress 70

    # Baloo Indexer
    if [ -n "$BALOO_CMD" ]; then
         log_action "[DESKTOP] Suspending and Disabling File Indexer ($BALOO_CMD)..."
         sudo -u $CURRENT_USER DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR" $BALOO_CMD suspend > /dev/null 2>&1
         sudo -u $CURRENT_USER DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR" $BALOO_CMD disable > /dev/null 2>&1
    fi

    # GPU
    gpu_tweaks "enable"
    progress 80

    # Network
    network_tweaks "enable"
    progress 90
    
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
    
    # 1. Compositor
    GM_START="${QDBUS_CMD} org.kde.KWin /Compositor suspend"
    GM_END="${QDBUS_CMD} org.kde.KWin /Compositor resume"
    
    # 2. Baloo
    if [ -n "$BALOO_CMD" ]; then
        GM_START="${GM_START} ; ${BALOO_CMD} suspend"
        GM_END="${GM_END} ; ${BALOO_CMD} resume"
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

    # RAM
    sysctl -w vm.swappiness=60 > /dev/null
    progress 50

    # DEEP KDE RESTORATION (Via Python Helper)
    SCRIPT_DIR=$(dirname "$0")
    PYTHON_HELPER="$SCRIPT_DIR/kde_booster.py"

    if [ -f "$PYTHON_HELPER" ]; then
        log_action "[PLASMA] Restoring default configuration..."
        sudo -u $CURRENT_USER python3 "$PYTHON_HELPER" off
    fi

    # Compositor Reload (Legacy Fallback)
    log_action "[DESKTOP] Reloading KWin settings..."
    sudo -u $CURRENT_USER DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR" $QDBUS_CMD org.kde.KWin /KWin reconfigure > /dev/null 2>&1
    sudo -u $CURRENT_USER DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR" $QDBUS_CMD org.kde.KWin /Compositor resume > /dev/null 2>&1
    
    # Baloo
    if [ -n "$BALOO_CMD" ]; then
         log_action "[DESKTOP] Resuming File Indexer..."
         sudo -u $CURRENT_USER DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR" $BALOO_CMD enable > /dev/null 2>&1
         sudo -u $CURRENT_USER DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR" $BALOO_CMD resume > /dev/null 2>&1
    fi
    
    progress 70

    # GPU & Network
    gpu_tweaks "disable"
    progress 80
    network_tweaks "disable"
    progress 90

    log_action "System Restored."
    progress 100
}

check_status() {
    GOVERNOR=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null)
    if [ "$GOVERNOR" == "performance" ]; then
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

    SWAP=$(cat /proc/sys/vm/swappiness 2>/dev/null)
    echo "Swappiness: $SWAP"

    # Compositor Check - Suppress errors if method not found
    RAW_SUSPEND=$(sudo -u $CURRENT_USER DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR" $QDBUS_CMD org.kde.KWin /Compositor isSuspended 2>/dev/null)
    if [[ "$RAW_SUSPEND" == "true" || "$RAW_SUSPEND" == "false" ]]; then
        IS_SUSPENDED="$RAW_SUSPEND"
    else
        IS_SUSPENDED="N/A"
    fi
    echo "Compositor Suspended: $IS_SUSPENDED"

    TCP=$(sysctl -n net.ipv4.tcp_congestion_control 2>/dev/null)
    echo "TCP Congestion: $TCP"
    
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
