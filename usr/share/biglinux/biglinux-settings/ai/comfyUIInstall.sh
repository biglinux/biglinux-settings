#!/bin/bash

#Translation
export TEXTDOMAINDIR="/usr/share/locale"
export TEXTDOMAIN=biglinux-settings

# Assign the received arguments to variables with clear names
function="$1"

# Starts Zenity IN THE BACKGROUND, as the user, with the full environment
if [[ "$function" == "install" ]]; then
  zenityTitle=$"comfyUI Install...."
  zenityText=$"Instaling comfyUI, this step take a long time, Please wait..."
elif [[ "$function" == "uninstall" ]]; then
  zenityTitle=$"Uninstall comfyUI...."
  zenityText=$"Uninstaling comfyUI, Please wait..."
fi

# Executes tasks.
updateTask() {
  if [[ "$function" == "install" ]]; then
    # clone and venv
    git clone https://github.com/Comfy-Org/ComfyUI.git $HOME/ComfyUI
    cd $HOME/ComfyUI
    python -m venv .

    # discover GPU
    vgaList=$(lspci | grep -iE "VGA|3D|Display")
    if [[ $(echo $vgaList | grep -Ei '(VGA|3D|Display).*(radeon|amd|\bati)') ]]; then
      gpu='amd'
    elif [[ $(echo $vgaList | grep -i nvidia) ]]; then
      gpu='nvidia'
    # elif [[ $(echo $vgaList | grep -i ????) ]]; then
    #     gpu='intel'
    # else
    #   gpu='cpu'
    fi

    # install GPU depends
    if [ -z "$gpu" ];then
      echo "GPU not found"
      exit 1
    #amd
    elif [ "$gpu" = "amd" ];then
      bin/pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm7.1
    #intel NPX
    elif [ "$gpu" = "intel" ];then
      bin/pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/xpu
    #nvidia
    elif [ "$gpu" = "nvidia" ];then
      bin/pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu130
    fi

    bin/pip install comfy-cli
    bash -c "yes | bin/comfy install --$gpu --restore"

    sleep 1
    echo "100" # Ensures Zenity closes
  else
    # stop service
    kill $(ps aux | grep -i "$HOME/ComfyUI/bin/python $HOME/ComfyUI/main.py" | grep -v grep | awk '{print $2}')
    # erase comfyUI folder
    rm -rf "$HOME/ComfyUI"

    sleep 1
    echo "100" # Ensures Zenity closes
  fi
  return 0
}
# updateTask > "$pipePath"
updateTask | zenity --progress --title="$zenityTitle" --text="$zenityText" --pulsate --auto-close --no-cancel

# CAPTURES THE STATUS OF THE FUNCTION (the first command in the pipe)
exitCode=${PIPESTATUS[0]}

# Shows the final result to the user, also with the correct theme.
if [[ "$exitCode" == "0" ]] && [[ "$function" == "install" ]]; then
  zenityText=$"comfyUI installed successfully"
  zenity --info --text="$zenityText"
elif [[ "$exitCode" == "0" ]] && [[ "$function" == "uninstall" ]]; then
  zenityText=$"comfyUI uninstalled successfully"
  zenity --info --text="$zenityText"
else
  zenityText=$"Failed to install comfyUI!"
  zenity --info --text="$zenityText"
fi

# Exits the script with the correct exit code
exit $exitCode
