#!/bin/bash

# -----------------------------------------------------------------------
# JamesDSP control script – user‑level entry point
# -----------------------------------------------------------------------
# This script performs state checks and delegates privileged actions
# (enable, disable) to jamesdspRun.sh via pkexec.
#
# The heavy lifting (package management, daemon communication, preset
# handling) is done in the privileged script, keeping this file simple
# and safe to run as a normal user.

# Function: check whether JamesDSP is installed and enabled
check_state() {
    # Check that the binary is available
    if ! command -v jamesdsp &>/dev/null; then
        echo "false"
        return
    fi

    # Ask the daemon if the master switch is on
    if jamesdsp --get master_enable 2>/dev/null | grep -q "true"; then
        echo "true"
    else
        echo "false"
    fi
}

# Function: toggle JamesDSP – enable or disable
#   $1 – desired state (true/false)
toggle_state() {
    new_state="$1"
    if [[ "$new_state" == "true" ]]; then
        # Enable (may install first)
        pkexec "$PWD/system/jamesdspRun.sh" "enable" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
        exitCode=$?
    else
        # Disable
        pkexec "$PWD/system/jamesdspRun.sh" "disable" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
        exitCode=$?
    fi
    exit $exitCode
}

# Main dispatcher
case "$1" in
    "check")
        check_state
        ;;
    "toggle")
        toggle_state "$2"
        ;;
    *)
        echo "Usage: $0 {check|toggle} [true|false]"
        echo "  check              - Print whether JamesDSP is enabled"
        echo "  toggle <state>     - Enable or disable JamesDSP (state: true|false)"
        exit 1
        ;;
esac
