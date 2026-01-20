#!/bin/bash

# JamesDSP management script

# Check if JamesDSP is installed and enabled
check_state() {
    # First check if jamesdsp is installed
    if ! command -v jamesdsp &> /dev/null; then
        echo "false"
        return
    fi
    
    # Check if daemon is running and enabled
    if pgrep -f "jamesdsp" > /dev/null 2>&1; then
        # Check if it's enabled
        if jamesdsp --get master_enable 2>/dev/null | grep -q "true"; then
            echo "true"
        else
            echo "false"
        fi
    else
        echo "false"
    fi
}

# Create BigLinux default preset if it doesn't exist
create_default_preset() {
    PRESET_DIR="$HOME/.config/jamesdsp/presets"
    PRESET_FILE="$PRESET_DIR/big-jamesdsp.conf"
    
    # Create directory if it doesn't exist
    mkdir -p "$PRESET_DIR"
    
    # Only create if preset doesn't exist
    if [ ! -f "$PRESET_FILE" ]; then
        echo "Creating BigLinux default preset..."
        cat > "$PRESET_FILE" << 'EOF'
bass_enable=false
bass_maxgain=4
compander_enable=false
compander_granularity=2
compander_response=95.0;200.0;400.0;800.0;1600.0;3400.0;7500.0;0;0;0;0;0;0;0
compander_time_freq_transforms=0
compander_timeconstant=0.22000
convolver_enable=true
convolver_file=.config/jamesdsp/irs/CorredHRTF_Surround2.wav
convolver_optimization_mode=2
convolver_waveform_edit=-80;-100;0;0;0;0
crossfeed_bs2b_fcut=700
crossfeed_bs2b_feed=60
crossfeed_enable=true
crossfeed_mode=4
ddc_enable=true
ddc_file=.config/jamesdsp/vdc/FrontRearContrast.vdc
graphiceq_enable=false
graphiceq_param=GraphicEQ: 20 0; 25 0; 31.5 0; 40 0; 50 0; 63 0; 80 0; 100 0; 125 0; 160 0; 200 0; 250 0; 315 0; 400 0; 500 0; 630 0; 800 0; 1000 0; 1250 0; 1600 0; 2000 0; 2500 0; 3150 0; 4000 0; 5000 0; 6300 0; 8000 0; 10000 0; 12500 0; 16000 0; 20000 0
liveprog_enable=true
liveprog_file=.config/jamesdsp/liveprog/fftConvolution2x4x2.eel
master_enable=true
master_limrelease=10
master_limthreshold=0
master_postgain=0
reverb_bassboost=0.10000
reverb_decay=1.80000
reverb_delay=0.00000
reverb_enable=false
reverb_finaldry=-12.00000
reverb_finalwet=-30.00000
reverb_lfo_spin=1.60000
reverb_lfo_wander=0.20000
reverb_lpf_bass=1000
reverb_lpf_damp=16000
reverb_lpf_input=18000
reverb_lpf_output=18000
reverb_osf=2
reverb_reflection_amount=0.00000
reverb_reflection_factor=1.00000
reverb_reflection_width=1.00000
reverb_wet=-8.00000
reverb_width=1.00000
stereowide_enable=false
stereowide_level=50
tone_enable=true
tone_eq=25.0;40.0;63.0;100.0;160.0;250.0;400.0;630.0;1000.0;1600.0;2500.0;4000.0;6300.0;10000.0;16000.0;-1.5;-2;-3;-3;-0.5;1.5;3.5;3.5;3.5;3;2;1.5;0;0;-1.5
tone_filtertype=0
tone_interpolation=1
tube_enable=false
tube_pregain=344
EOF
        echo "BigLinux default preset created: big-jamesdsp"
    fi
}

# Install JamesDSP if needed
install_jamesdsp() {
    echo "Installing JamesDSP..."
    
    # Check if it's already installed
    if command -v jamesdsp &> /dev/null; then
        echo "JamesDSP is already installed."
        create_default_preset
        return 0
    fi
    
    # Try to install via package manager
    # Using pkexec for graphical sudo prompt
    if pkexec pacman -S --noconfirm jamesdsp; then
        echo "JamesDSP installed successfully."
        create_default_preset
        return 0
    else
        echo "Failed to install JamesDSP."
        return 1
    fi
}

# Enable JamesDSP
enable_jamesdsp() {
    # Ensure default preset exists
    create_default_preset
    
    # Check if daemon is already running
    if ! pgrep -f "jamesdsp" > /dev/null 2>&1; then
        echo "JamesDSP daemon not running. It should be started via GUI."
        # Don't fail - daemon will be started by GUI before calling enable
        return 0
    fi
    
    # Daemon is running - try to enable it
    if jamesdsp --set master_enable=true > /dev/null 2>&1; then
        echo "JamesDSP enabled."
        return 0
    else
        # Command failed but daemon is running - still return success
        # The setting might already be enabled
        echo "JamesDSP enable command had issues, but continuing..."
        return 0
    fi
}

# Disable JamesDSP (just turn off, don't kill daemon)
disable_jamesdsp() {
    # If daemon is not running, consider it already disabled (success)
    if ! pgrep -f "jamesdsp" > /dev/null 2>&1; then
        echo "JamesDSP daemon not running (already disabled)."
        return 0
    fi
    
    # Daemon is running - try to disable it
    if jamesdsp --set master_enable=false > /dev/null 2>&1; then
        echo "JamesDSP disabled (master_enable=false)."
        return 0
    else
        # Command failed but daemon is running
        # Still return success - setting might already be false
        echo "JamesDSP disable command had issues, but continuing..."
        return 0
    fi
}

# Toggle JamesDSP state
toggle_state() {
    new_state="$1"
    
    if [[ "$new_state" == "true" ]]; then
        # Check if installed first
        if ! command -v jamesdsp &> /dev/null; then
            install_jamesdsp || exit 1
        fi
        
        # Enable JamesDSP
        enable_jamesdsp
        exitCode=$?
    else
        # Disable JamesDSP (this is the "just disable" option)
        disable_jamesdsp
        exitCode=$?
    fi
    
    exit $exitCode
}

# Remove JamesDSP package only
remove_package() {
    echo "Stopping JamesDSP..."
    
    # Stop systemd services if they exist
    if systemctl --user is-active --quiet jamesdsp 2>/dev/null; then
        systemctl --user stop jamesdsp
        sleep 0.5
    fi
    
    if systemctl is-active --quiet jamesdsp 2>/dev/null; then
        pkexec systemctl stop jamesdsp 2>/dev/null
        sleep 0.5
    fi
    
    # Kill the daemon (multiple attempts)
    # Use -x to match exact process name 'jamesdsp' to avoid killing this script (jamesdsp.sh)
    for i in {1..3}; do
        pkill -x jamesdsp 2>/dev/null
        sleep 0.5
    done
    
    # Force kill if still running
    if pgrep -x jamesdsp > /dev/null; then
        echo "Force killing remaining processes..."
        pkill -9 -x jamesdsp 2>/dev/null
        sleep 1
    fi
    
    echo "Removing package..."
    
    # Check if package is installed first (both official and AUR packages)
    if ! pacman -Q jamesdsp 2>/dev/null && ! pacman -Qm jamesdsp 2>/dev/null; then
        echo "Package not installed (already removed or never installed)."
        return 0
    fi
    
    # Try to remove the package with different strategies
    local removed=false
    
    # Strategy 1: Normal removal
    echo "Attempting normal removal..."
    if pkexec pacman -R --noconfirm jamesdsp 2>/dev/null; then
        echo "Package removed successfully."
        removed=true
    fi
    
    # Strategy 2: Remove with unneeded dependencies
    if [ "$removed" = false ]; then
        echo "Attempting removal with dependencies..."
        if pkexec pacman -Rns --noconfirm jamesdsp 2>/dev/null; then
            echo "Package removed with dependencies."
            removed=true
        fi
    fi
    
    # Strategy 3: Force removal ignoring dependencies
    if [ "$removed" = false ]; then
        echo "Attempting forced removal..."
        if pkexec pacman -Rdd --noconfirm jamesdsp 2>/dev/null; then
            echo "Package force removed."
            removed=true
        fi
    fi
    
    # Strategy 4: Check if it's an AUR package
    if [ "$removed" = false ] && pacman -Qm jamesdsp &>/dev/null; then
        echo "Detected AUR package, trying AUR helpers..."
        
        if command -v yay &>/dev/null && yay -R --noconfirm jamesdsp 2>/dev/null; then
            echo "Package removed using yay."
            removed=true
        elif command -v paru &>/dev/null && paru -R --noconfirm jamesdsp 2>/dev/null; then
            echo "Package removed using paru."
            removed=true
        fi
    fi
    
    # Final verification
    if [ "$removed" = true ] || (! pacman -Q jamesdsp 2>/dev/null && ! pacman -Qm jamesdsp 2>/dev/null); then
        echo "✓ Package removal verified."
        return 0
    else
        echo "✗ Failed to remove package. It may be locked or broken."
        echo "   You may need to manually remove it with:"
        echo "   sudo pacman -Rdd jamesdsp"
        echo "   or check with: pacman -Q | grep -i james"
        return 1
    fi
}

# Remove dotfiles only
remove_dotfiles() {
    echo "Cleaning configuration files..."
    rm -rf "$HOME/.config/jamesdsp"
    rm -rf "$HOME/.local/share/jamesdsp"
    echo "Configuration files removed."
}

# Remove JamesDSP completely (package + dotfiles)
remove_complete() {
    remove_package
    remove_dotfiles
    echo "JamesDSP removed completely."
}

# Main script logic
case "$1" in
    "check")
        check_state
        ;;
    "toggle")
        toggle_state "$2"
        ;;
    "install")
        install_jamesdsp
        ;;
    "remove_complete")
        remove_complete
        ;;
    "remove_package")
        remove_package
        ;;
    "remove_dotfiles")
        remove_dotfiles
        ;;
    *)
        echo "Usage: $0 {check|toggle|install|remove_complete|remove_package|remove_dotfiles} [true|false]"
        echo "  check             - Check current status"
        echo "  toggle <state>    - Enable or disable JamesDSP"
        echo "  install           - Install JamesDSP"
        echo "  remove_package    - Remove JamesDSP package only"
        echo "  remove_dotfiles   - Remove configuration files only"
        echo "  remove_complete   - Remove JamesDSP package and all config files"
        exit 1
        ;;
esac
