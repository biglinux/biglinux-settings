#!/bin/bash

# GameMode Configuration Script
# Manages gamemode.ini settings based on hardware detection

CONFIG_FILE="$HOME/.config/gamemode.ini"

# --- HARDWARE DETECTION ---
# --- HARDWARE DETECTION HELPER ---
init_detection() {
    local cpu_model gpu_vendors
    cpu_model=$(grep -m 1 "model name" /proc/cpuinfo)
    gpu_vendors=$(lspci | grep -E "VGA|3D")
    
    # CPU Detection
    IS_INTEL_HYBRID=false
    if lscpu | grep -i "Model name" | grep -E "12th|13th|14th|Core Ultra" > /dev/null; then
        IS_INTEL_HYBRID=true
    fi
    
    IS_AMD_X3D=false
    if echo "$cpu_model" | grep -i "X3D" > /dev/null; then
        IS_AMD_X3D=true
    fi
    
    IS_AMD_DUAL_CCD=false
    if echo "$cpu_model" | grep -iE "7950X3D|9950X3D" > /dev/null; then
        IS_AMD_DUAL_CCD=true
    fi
    
    HAS_X3D_DRIVER=false
    if [[ -f /sys/devices/system/cpu/amd_x3d_mode/mode ]]; then
        HAS_X3D_DRIVER=true
    fi
    
    # Display Server Detection
    DISPLAY_SERVER="unknown"
    if [[ -n "$WAYLAND_DISPLAY" ]]; then
        DISPLAY_SERVER="wayland"
    elif [[ -n "$DISPLAY" ]]; then
        DISPLAY_SERVER="x11"
    fi
    
    # GPU Detection
    HAS_NVIDIA=false
    if echo "$gpu_vendors" | grep -iq "NVIDIA"; then
        HAS_NVIDIA=true
    fi
    
    HAS_AMD=false
    if echo "$gpu_vendors" | grep -iq "AMD"; then
        HAS_AMD=true
    fi
    
    HAS_INTEL_IGPU=false
    if echo "$gpu_vendors" | grep -iq "Intel"; then
        HAS_INTEL_IGPU=true
    fi
    
    HAS_INTEL_ONLY=false
    if [[ "$HAS_INTEL_IGPU" == "true" && "$HAS_NVIDIA" == "false" && "$HAS_AMD" == "false" ]]; then
        HAS_INTEL_ONLY=true
    fi
}

detect_hardware() {
    init_detection
    
    # Output key=value pairs
    echo "display_server=$DISPLAY_SERVER"
    
    # CPU info
    if [[ "$IS_INTEL_HYBRID" == "true" ]]; then
        echo "cpu_type=intel_hybrid"
        echo "cpu_supports_pin_cores=true"
        echo "cpu_supports_park_cores=true"
    elif [[ "$IS_AMD_X3D" == "true" ]]; then
        echo "cpu_type=amd_x3d"
        echo "cpu_supports_pin_cores=true"
        echo "cpu_supports_park_cores=false"
    else
        echo "cpu_type=standard"
        echo "cpu_supports_pin_cores=false"
        echo "cpu_supports_park_cores=false"
    fi
    
    # AMD Dual CCD X3D support
    if [[ "$IS_AMD_DUAL_CCD" == "true" ]] && [[ "$HAS_X3D_DRIVER" == true ]]; then
        echo "supports_amd_x3d_mode=true"
    else
        echo "supports_amd_x3d_mode=false"
    fi
    
    # Split lock mitigation (modern CPUs)
    echo "supports_disable_splitlock=true"
    
    # GPU info
    echo "has_nvidia=$HAS_NVIDIA"
    echo "has_amd=$HAS_AMD"
    echo "has_intel_igpu=$HAS_INTEL_IGPU"
    echo "has_intel_only=$HAS_INTEL_ONLY"
}

# --- READ CURRENT CONFIG ---
read_config() {
    if [[ ! -f "$CONFIG_FILE" ]]; then
        # Return defaults if file doesn't exist
        echo "exists=false"
        return
    fi
    
    echo "exists=true"
    
    # Parse the config file
    local section=""
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Skip empty lines and comments
        [[ -z "$line" || "$line" =~ ^[[:space:]]*\; ]] && continue
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        
        # Check for section
        if [[ "$line" =~ ^\[([^\]]+)\] ]]; then
            section="${BASH_REMATCH[1]}"
            continue
        fi
        
        # Parse key=value
        if [[ "$line" =~ ^([^=]+)=(.*)$ ]]; then
            local key="${BASH_REMATCH[1]}"
            local value="${BASH_REMATCH[2]}"
            # Trim whitespace
            key=$(echo "$key" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
            value=$(echo "$value" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
            
            case "$section" in
                "general")
                    case "$key" in
                        "reaper_freq"|"desiredgov"|"defaultgov"|"desiredprof"|"defaultprof"|"igpu_desiredgov"|"igpu_power_threshold"|"softrealtime"|"renice"|"ioprio"|"inhibit_screensaver"|"disable_splitlock")
                            echo "$key=$value"
                            ;;
                    esac
                    ;;
                "cpu")
                    case "$key" in
                        "pin_cores"|"park_cores"|"amd_x3d_mode_desired"|"amd_x3d_mode_default")
                            echo "$key=$value"
                            ;;
                    esac
                    ;;
                "gpu")
                    case "$key" in
                        "apply_gpu_optimisations"|"gpu_device"|"nv_powermizer_mode"|"nv_core_clock_mhz_offset"|"nv_mem_clock_mhz_offset"|"amd_performance_level")
                            echo "$key=$value"
                            ;;
                    esac
                    ;;
            esac
        fi
    done < "$CONFIG_FILE"
}

# --- WRITE OPTION ---
# Usage: write_option <key> <value>
write_option() {
    local key="$1"
    local value="$2"
    
    # Ensure config file exists with base structure
    if [[ ! -f "$CONFIG_FILE" ]]; then
        create_base_config
    fi
    
    # Determine section for the key
    local section
    local actual_key="$key"
    case "$key" in
        "reaper_freq"|"desiredgov"|"defaultgov"|"desiredprof"|"defaultprof"|"igpu_desiredgov"|"igpu_power_threshold"|"softrealtime"|"renice"|"ioprio"|"inhibit_screensaver"|"disable_splitlock")
            section="general"
            ;;
        "pin_cores"|"park_cores"|"amd_x3d_mode_desired"|"amd_x3d_mode_default")
            section="cpu"
            ;;
        "apply_gpu_optimisations"|"gpu_device"|"nv_powermizer_mode"|"nv_core_clock_mhz_offset"|"nv_mem_clock_mhz_offset"|"amd_performance_level")
            section="gpu"
            ;;
        *)
            echo "Unknown key: $key"
            return 1
            ;;
    esac
    
    # Create temp file
    local temp_file
    temp_file=$(mktemp)
    
    local in_section=false
    local key_found=false
    local section_exists=false
    local current_section=""
    
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Check for section header
        if [[ "$line" =~ ^\[([^\]]+)\] ]]; then
            current_section="${BASH_REMATCH[1]}"
            
            # If we were in the target section and didn't find the key, add it
            if [[ "$in_section" == true && "$key_found" == false ]]; then
                echo "$actual_key=$value" >> "$temp_file"
                key_found=true
            fi
            
            if [[ "$current_section" == "$section" ]]; then
                in_section=true
                section_exists=true
            else
                in_section=false
            fi
            
            echo "$line" >> "$temp_file"
            continue
        fi
        
        # If in target section, check for key (handle commented keys too)
        if [[ "$in_section" == true ]] && [[ "$line" =~ ^[[:space:]]*\;?$actual_key[[:space:]]*= ]]; then
            echo "$actual_key=$value" >> "$temp_file"
            key_found=true
            continue
        fi
        
        echo "$line" >> "$temp_file"
    done < "$CONFIG_FILE"
    
    # If section was the last one and key wasn't found
    if [[ "$in_section" == true && "$key_found" == false ]]; then
        echo "$actual_key=$value" >> "$temp_file"
        key_found=true
    fi
    
    # If section doesn't exist, add it at the end
    if [[ "$section_exists" == false ]]; then
        echo "" >> "$temp_file"
        echo "[$section]" >> "$temp_file"
        echo "$actual_key=$value" >> "$temp_file"
    fi
    
    mv "$temp_file" "$CONFIG_FILE"
    
    # Reload GameMode (non-blocking with timeout)
    timeout 2 gamemoded -r &>/dev/null &
    
    echo "ok"
}

# --- REMOVE OPTION ---
# Usage: remove_option <key>
remove_option() {
    local key="$1"
    
    if [[ ! -f "$CONFIG_FILE" ]]; then
        echo "ok"
        return
    fi
    
    # Handle custom key naming
    local actual_key="$key"
    
    
    # Create temp file
    local temp_file
    temp_file=$(mktemp)
    
    # Remove the line with the key (including commented versions)
    grep -v "^[[:space:]]*;*${actual_key}=" "$CONFIG_FILE" > "$temp_file"
    
    mv "$temp_file" "$CONFIG_FILE"
    
    # Reload GameMode (non-blocking with timeout)
    timeout 2 gamemoded -r &>/dev/null &
    
    echo "ok"
}

# --- CREATE BASE CONFIG ---
create_base_config() {
    init_detection
    mkdir -p "$(dirname "$CONFIG_FILE")"
    
    # Start General Section
    echo "[general]" > "$CONFIG_FILE"
    echo "reaper_freq=5" >> "$CONFIG_FILE"
    echo "desiredgov=performance" >> "$CONFIG_FILE"
    echo "desiredprof=performance" >> "$CONFIG_FILE"
    
    # iGPU settings - only if iGPU or AMD APU present
    if [[ "$HAS_INTEL_IGPU" == "true" ]] || [[ "$HAS_AMD" == "true" ]]; then
        echo "igpu_desiredgov=powersave" >> "$CONFIG_FILE"
        echo "igpu_power_threshold=0.3" >> "$CONFIG_FILE"
    fi
    
    echo "softrealtime=auto" >> "$CONFIG_FILE"
    echo "renice=10" >> "$CONFIG_FILE"
    echo "ioprio=0" >> "$CONFIG_FILE"
    echo "inhibit_screensaver=1" >> "$CONFIG_FILE"
    echo "disable_splitlock=1" >> "$CONFIG_FILE"
    echo "" >> "$CONFIG_FILE"
    
    # Filter Section
    echo "[filter]" >> "$CONFIG_FILE"
    echo ";whitelist=RiseOfTheTombRaider" >> "$CONFIG_FILE"
    echo ";blacklist=HalfLife3" >> "$CONFIG_FILE"
    echo ";glxgears" >> "$CONFIG_FILE"
    echo "" >> "$CONFIG_FILE"
    
    # GPU Section
    echo "[gpu]" >> "$CONFIG_FILE"
    # Always include the disclaimer/responsibility key
    echo ";apply_gpu_optimisations=accept-responsibility" >> "$CONFIG_FILE"
    echo "gpu_device=0" >> "$CONFIG_FILE"
    
    # Nvidia Options
    if [[ "$HAS_NVIDIA" == "true" ]]; then
        if [[ "$DISPLAY_SERVER" == "x11" ]]; then
            echo ";nv_powermizer_mode=1" >> "$CONFIG_FILE"
            echo "nv_core_clock_mhz_offset=0" >> "$CONFIG_FILE"
            echo "nv_mem_clock_mhz_offset=0" >> "$CONFIG_FILE"
            echo "nv_per_profile_editable=1" >> "$CONFIG_FILE"
        else
            echo "; Nvidia options disabled (Wayland/Non-X11 detected)" >> "$CONFIG_FILE"
        fi
    fi
    
    # AMD Options
    if [[ "$HAS_AMD" == "true" ]]; then
        echo "amd_performance_level=high" >> "$CONFIG_FILE"
    fi
    echo "" >> "$CONFIG_FILE"
    
    # CPU Section
    echo "[cpu]" >> "$CONFIG_FILE"
    
    # Pin Cores (Intel Hybrid, AMD X3D)
    if [[ "$IS_INTEL_HYBRID" == "true" ]] || [[ "$IS_AMD_X3D" == "true" ]]; then
        echo "pin_cores=yes" >> "$CONFIG_FILE"
    else
        echo "pin_cores=no" >> "$CONFIG_FILE"
    fi
    
    # Park Cores (Intel Hybrid only)
    if [[ "$IS_INTEL_HYBRID" == "true" ]]; then
        echo "park_cores=no" >> "$CONFIG_FILE"
    else
        echo ";park_cores=no" >> "$CONFIG_FILE"
    fi
    
    # AMD X3D Mode
    if [[ "$IS_AMD_DUAL_CCD" == "true" ]] && [[ "$HAS_X3D_DRIVER" == "true" ]]; then
        echo "amd_x3d_mode_desired=frequency" >> "$CONFIG_FILE"
        echo "amd_x3d_mode_default=cache" >> "$CONFIG_FILE"
    fi
    echo "" >> "$CONFIG_FILE"
    
    # Supervisor Section
    echo "[supervisor]" >> "$CONFIG_FILE"
    echo ";supervisor_whitelist=" >> "$CONFIG_FILE"
    echo ";supervisor_blacklist=" >> "$CONFIG_FILE"
    echo "require_supervisor=0" >> "$CONFIG_FILE"
    
    echo "ok"
}

# --- MAIN ---
case "$1" in
    "detect")
        detect_hardware
        ;;
    "read")
        read_config
        ;;
    "write")
        write_option "$2" "$3"
        ;;
    "remove")
        remove_option "$2"
        ;;
    "create")
        create_base_config
        ;;
    *)
        echo "Usage: $0 {detect|read|write|remove|create}"
        echo "  detect           - Detect hardware and return key=value pairs"
        echo "  read             - Read current config as key=value pairs"
        echo "  write <key> <val>- Write option to config"
        echo "  remove <key>     - Remove option from config"
        echo "  create           - Create base config file"
        exit 1
        ;;
esac
