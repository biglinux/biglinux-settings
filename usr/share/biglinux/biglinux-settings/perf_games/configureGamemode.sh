#!/bin/bash
# GameMode Configuration Script
config_file="$HOME/.config/gamemode.ini"

init_detection() {
    local cpu_model gpu_vendors
    cpu_model=$(grep -m 1 "model name" /proc/cpuinfo)
    gpu_vendors=$(lspci | grep -E "VGA|3D")
    
    is_intel_hybrid=false
    if lscpu | grep -i "Model name" | grep -E "12th|13th|14th|Core Ultra" > /dev/null; then is_intel_hybrid=true; fi
    
    is_amd_x3d=false
    if echo "$cpu_model" | grep -i "X3D" > /dev/null; then is_amd_x3d=true; fi
    
    is_amd_dual_ccd=false
    if echo "$cpu_model" | grep -iE "7950X3D|9950X3D" > /dev/null; then is_amd_dual_ccd=true; fi
    
    has_x3d_driver=false
    if [[ -f /sys/devices/system/cpu/amd_x3d_mode/mode ]]; then has_x3d_driver=true; fi
    
    display_server="unknown"
    [[ -n "$WAYLAND_DISPLAY" ]] && display_server="wayland" || { [[ -n "$DISPLAY" ]] && display_server="x11"; }
    
    has_nvidia=false; echo "$gpu_vendors" | grep -iq "NVIDIA" && has_nvidia=true
    has_amd=false; echo "$gpu_vendors" | grep -iq "AMD" && has_amd=true
    has_intel_igpu=false; echo "$gpu_vendors" | grep -iq "Intel" && has_intel_igpu=true
    
    has_intel_only=false
    [[ "$has_intel_igpu" == "true" && "$has_nvidia" == "false" && "$has_amd" == "false" ]] && has_intel_only=true
}

detect_hardware() {
    init_detection
    echo "display_server=$display_server"
    
    if [[ "$is_intel_hybrid" == "true" ]]; then
        echo -e "cpu_type=intel_hybrid\ncpu_supports_pin_cores=true\ncpu_supports_park_cores=true"
    elif [[ "$is_amd_x3d" == "true" ]]; then
        echo -e "cpu_type=amd_x3d\ncpu_supports_pin_cores=true\ncpu_supports_park_cores=false"
    else
        echo -e "cpu_type=standard\ncpu_supports_pin_cores=false\ncpu_supports_park_cores=false"
    fi
    
    if [[ "$is_amd_dual_ccd" == "true" ]] && [[ "$has_x3d_driver" == true ]]; then echo "supports_amd_x3d_mode=true"; else echo "supports_amd_x3d_mode=false"; fi
    
    echo "supports_disable_splitlock=true"
    echo -e "has_nvidia=$has_nvidia\nhas_amd=$has_amd\nhas_intel_igpu=$has_intel_igpu\nhas_intel_only=$has_intel_only"
}

read_config() {
    [[ ! -f "$config_file" ]] && echo "exists=false" && return
    echo "exists=true"
    
    local section=""
    while IFS= read -r line || [[ -n "$line" ]]; do
        [[ -z "$line" || "$line" =~ ^[[:space:]]*\; || "$line" =~ ^[[:space:]]*# ]] && continue
        
        if [[ "$line" =~ ^\[([^\]]+)\] ]]; then section="${BASH_REMATCH[1]}"; continue; fi
        
        if [[ "$line" =~ ^([^=]+)=(.*)$ ]]; then
            local key="${BASH_REMATCH[1]}" value="${BASH_REMATCH[2]}"
            key=$(echo "$key" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
            value=$(echo "$value" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
            
            case "$section" in
                "general") [[ "$key" =~ ^(reaper_freq|desiredgov|defaultgov|desiredprof|defaultprof|igpu_desiredgov|igpu_power_threshold|softrealtime|renice|ioprio|inhibit_screensaver|disable_splitlock)$ ]] && echo "$key=$value" ;;
                "cpu") [[ "$key" =~ ^(pin_cores|park_cores|amd_x3d_mode_desired|amd_x3d_mode_default)$ ]] && echo "$key=$value" ;;
                "gpu") [[ "$key" =~ ^(apply_gpu_optimisations|gpu_device|nv_powermizer_mode|nv_core_clock_mhz_offset|nv_mem_clock_mhz_offset|amd_performance_level)$ ]] && echo "$key=$value" ;;
            esac
        fi
    done < "$config_file"
}

write_option() {
    local key="$1" value="$2" section
    [[ ! -f "$config_file" ]] && create_base_config
    
    case "$key" in
        "reaper_freq"|"desiredgov"|"defaultgov"|"desiredprof"|"defaultprof"|"igpu_desiredgov"|"igpu_power_threshold"|"softrealtime"|"renice"|"ioprio"|"inhibit_screensaver"|"disable_splitlock") section="general" ;;
        "pin_cores"|"park_cores"|"amd_x3d_mode_desired"|"amd_x3d_mode_default") section="cpu" ;;
        "apply_gpu_optimisations"|"gpu_device"|"nv_powermizer_mode"|"nv_core_clock_mhz_offset"|"nv_mem_clock_mhz_offset"|"amd_performance_level") section="gpu" ;;
        *) echo "Unknown key: $key"; return 1 ;;
    esac
    
    local temp_file; temp_file=$(mktemp)
    local in_section=false key_found=false section_exists=false current_section=""
    
    while IFS= read -r line || [[ -n "$line" ]]; do
        if [[ "$line" =~ ^\[([^\]]+)\] ]]; then
            current_section="${BASH_REMATCH[1]}"
            if [[ "$in_section" == true && "$key_found" == false ]]; then echo "$key=$value" >> "$temp_file"; key_found=true; fi
            if [[ "$current_section" == "$section" ]]; then in_section=true; section_exists=true; else in_section=false; fi
            echo "$line" >> "$temp_file"
            continue
        fi
        
        if [[ "$in_section" == true ]] && [[ "$line" =~ ^[[:space:]]*\;?$key[[:space:]]*= ]]; then
            echo "$key=$value" >> "$temp_file"; key_found=true; continue
        fi
        echo "$line" >> "$temp_file"
    done < "$config_file"
    
    [[ "$in_section" == true && "$key_found" == false ]] && echo "$key=$value" >> "$temp_file"
    [[ "$section_exists" == false ]] && echo -e "\n[$section]\n$key=$value" >> "$temp_file"
    
    mv "$temp_file" "$config_file"
    timeout 2 gamemoded -r &>/dev/null &
    echo "ok"
}

remove_option() {
    local key="$1"
    [[ ! -f "$config_file" ]] && echo "ok" && return
    local temp_file; temp_file=$(mktemp)
    grep -v "^[[:space:]]*;*${key}=" "$config_file" > "$temp_file"
    mv "$temp_file" "$config_file"
    timeout 2 gamemoded -r &>/dev/null &
    echo "ok"
}

create_base_config() {
    init_detection
    mkdir -p "$(dirname "$config_file")"
    
    echo -e "[general]\nreaper_freq=5\ndesiredgov=performance\ndesiredprof=performance" > "$config_file"
    
    if [[ "$has_intel_igpu" == "true" ]] || [[ "$has_amd" == "true" ]]; then
        echo -e "igpu_desiredgov=powersave\nigpu_power_threshold=0.3" >> "$config_file"
    fi
    
    echo -e "softrealtime=auto\nrenice=10\nioprio=0\ninhibit_screensaver=1\ndisable_splitlock=1\n\n[filter]\n\n[gpu]\ngpu_device=0" >> "$config_file"
    
    if [[ "$has_nvidia" == "true" ]] && [[ "$display_server" == "x11" ]]; then
        echo -e "nv_core_clock_mhz_offset=0\nnv_mem_clock_mhz_offset=0\nnv_per_profile_editable=1" >> "$config_file"
    fi
    
    [[ "$has_amd" == "true" ]] && echo "amd_performance_level=high" >> "$config_file"
    
    echo -e "\n[cpu]" >> "$config_file"
    
    if [[ "$is_intel_hybrid" == "true" ]] || [[ "$is_amd_x3d" == "true" ]]; then echo "pin_cores=yes" >> "$config_file"; else echo "pin_cores=no" >> "$config_file"; fi
    
    [[ "$is_intel_hybrid" == "true" ]] && echo "park_cores=no" >> "$config_file"
    
    if [[ "$is_amd_dual_ccd" == "true" ]] && [[ "$has_x3d_driver" == "true" ]]; then
        echo -e "amd_x3d_mode_desired=frequency\namd_x3d_mode_default=cache" >> "$config_file"
    fi
    
    echo -e "\n[supervisor]\nrequire_supervisor=0" >> "$config_file"
    echo "ok"
}

case "$1" in
    "detect") detect_hardware ;;
    "read") read_config ;;
    "write") write_option "$2" "$3" ;;
    "remove") remove_option "$2" ;;
    "create") create_base_config ;;
    *) exit 1 ;;
esac
