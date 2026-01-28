#!/bin/bash

# check current status
check_state() {
  if [[ -d "$HOME/.local/share/krita/pykrita/ai_diffusion" ]] && pacman -Q krita &>/dev/null; then
    echo "true"
  else
    echo "false"
  fi
}

# change the state
toggle_state() {
  new_state="$1"
  if [[ "$new_state" == "true" ]];then
    if ! pacman -Q krita &>/dev/null; then
      pkexec $PWD/ai/kritaRun.sh "install" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    fi
    killall krita
    diffusionUrl=$(curl -s "https://api.github.com/repos/Acly/krita-ai-diffusion/releases/latest" | grep "browser_download_url" | grep ".zip" | head -n 1 | cut -d '"' -f 4)
    wget $diffusionUrl -O /tmp/krita_ai_diffusion.zip
    7z x /tmp/krita_ai_diffusion.zip -o${HOME}/.local/share/krita/pykrita/
    rm /tmp/krita_ai_diffusion.zip
    mkdir -p $HOME/.local/share/krita/actions/
    cp $HOME/.local/share/krita/pykrita/ai_diffusion/ai_diffusion.action $HOME/.local/share/krita/actions/
    kwriteconfig6 --file kritarc --group "python" --key "enable_ai_diffusion" "true"

    zenityText=$"Generative AI for Krita has been successfully installed.\n\nOpen Krita, open an existing drawing or create a new one.\nIn the top panel go to Settings > Panels > check the AI Image Generation box.\n\nIn the window that opens on the bottom right.\nClick Configure > Local Managed Server, choose your GPU or CPU, choose the model in Workloads and click Install."
    zenity --info --text="$zenityText" --width=400 --height=300

    exitCode=$?
  else
    killall krita
    rm -rf "${HOME}/.local/share/krita/pykrita"
    rm -rf "${HOME}/.local/share/krita/ai_diffusion/server/models"
    rm -rf "${HOME}/.local/share/krita/ai_diffusion/server/venv"
    kwriteconfig6 --file kritarc --group "python" --key "enable_ai_diffusion" "false"
    exitCode=$?
  fi
  exit $exitCode
}

# Executes the function based on the parameter
case "$1" in
    "check")
        check_state
        ;;
    "toggle")
        toggle_state "$2"
        ;;
    *)
        echo "Use: $0 {check|toggle} [true|false]"
        echo "  check          - Check current status"
        echo "  toggle <state> - Changes to the specified state"
        exit 1
        ;;
esac
