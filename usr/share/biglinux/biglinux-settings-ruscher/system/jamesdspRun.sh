#!/bin/bash

# JamesDSP privileged helper script
# Executed with root privileges via pkexec.
# Performs installation, enable/disable, and removal tasks
# and copies the default preset from /etc/skel.

# Parse arguments
operation="$1"
user="$2"
display="$3"
xauthority="$4"
dbusSessionBusAddress="$5"
lang="$6"
language="$7"

userHome=$(eval echo "~$user")

# Helper to run a command as the original user with the full environment
runAsUser() {
    local cmd="$1"
    runuser -l "$user" -c "export DISPLAY='$display'; export XAUTHORITY='$xauthority'; export DBUS_SESSION_BUS_ADDRESS='$dbusSessionBusAddress'; export LANG='$lang'; export LANGUAGE='$language'; $cmd"
}

# Install JamesDSP package
installJamesdsp() {
    pacman -S --noconfirm jamesdsp
}

# Enable JamesDSP (ensure preset exists and set master_enable=true)
enableJamesdsp() {
    if ! command -v jamesdsp &>/dev/null; then
        installJamesdsp
    fi
    runAsUser "mkdir -p '$userHome/.config/jamesdsp/presets' && cp /etc/skel/.config/jamesdsp/presets/big-jamesdsp.conf '$userHome/.config/jamesdsp/presets/big-jamesdsp.conf'"
    runAsUser "jamesdsp --set master_enable=true"
}

# Disable JamesDSP (set master_enable=false)
disableJamesdsp() {
    runAsUser "jamesdsp --set master_enable=false"
}

# Stop and remove JamesDSP package
removePackage() {
    if systemctl --user is-active --quiet jamesdsp 2>/dev/null; then
        systemctl --user stop jamesdsp
    fi
    if systemctl is-active --quiet jamesdsp 2>/dev/null; then
        systemctl stop jamesdsp
    fi
    pkill -x jamesdsp 2>/dev/null || true
    pkill -9 -x jamesdsp 2>/dev/null || true
    pacman -Rdd --noconfirm jamesdsp
}

# Remove user configuration files
removeDotfiles() {
    runAsUser "rm -rf '$userHome/.config/jamesdsp' '$userHome/.local/share/jamesdsp'"
}

# Remove everything (package + config files)
removeComplete() {
    removePackage
    removeDotfiles
}

# Execute requested operation
case "$operation" in
    "install")
        installJamesdsp
        ;;
    "enable")
        enableJamesdsp
        ;;
    "disable")
        disableJamesdsp
        ;;
    "remove_package")
        removePackage
        ;;
    "remove_dotfiles")
        removeDotfiles
        ;;
    "remove_complete")
        removeComplete
        ;;
    *)
        echo "Unknown operation: $operation" >&2
        exit 1
        ;;
esac
