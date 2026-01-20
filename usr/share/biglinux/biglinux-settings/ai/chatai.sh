#!/bin/bash

# ChatAI Plasmoid Installation Script
# This script manages the installation and removal of the ChatAI Plasmoid for KDE Plasma

ACTION="${1:-install}"

install_chatai() {
    echo "Downloading ChatAI Plasmoid..."
    
    # Download the plasmoid
    if ! wget -O /tmp/chatai.zip https://github.com/DenysMb/ChatAI-Plasmoid/archive/refs/heads/main.zip; then
        echo "ERROR: Failed to download ChatAI Plasmoid"
        exit 1
    fi
    
    echo "Installing ChatAI Plasmoid..."
    
    # Try to install, if it fails, try to upgrade
    if ! kpackagetool6 -t Plasma/Applet -i /tmp/chatai.zip; then
        echo "Package already exists, attempting upgrade..."
        if ! kpackagetool6 -t Plasma/Applet -u /tmp/chatai.zip; then
            echo "ERROR: Failed to install or upgrade ChatAI Plasmoid"
            exit 1
        fi
    fi
    
    echo "Adding ChatAI widget to panel..."
    
    # Unlock desktop editing mode
    qdbus6 org.kde.plasmashell /PlasmaShell evaluateScript "lockCorona(false)"
    
    # Add widget to panel
    qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
        var allPanels = panels();
        for (var i = 0; i < allPanels.length; i++) {
            allPanels[i].addWidget('ChatAI-Plasmoid');
        }
    "
    
    # Lock desktop editing mode again
    qdbus6 org.kde.plasmashell /PlasmaShell evaluateScript "lockCorona(true)"
    
    # Clean up
    rm -f /tmp/chatai.zip
    
    echo "ChatAI Plasmoid installed successfully!"
}

remove_chatai() {
    echo "Removing ChatAI Plasmoid from configuration..."
    
    # Unlock desktop editing mode
    qdbus6 org.kde.plasmashell /PlasmaShell evaluateScript "lockCorona(false)"
    
    # Create temporary Python script for removal
    cat > /tmp/remove_chatai.py << 'PYTHON_SCRIPT'
import os
import sys

# Caminho do arquivo de configuração do Plasma
config_path = os.path.expanduser("~/.config/plasma-org.kde.plasma.desktop-appletsrc")

# Verifica se existe
if not os.path.exists(config_path):
    print("Arquivo de configuração não encontrado.")
    sys.exit(1)

print(f"Lendo: {config_path}")

with open(config_path, "r") as f:
    lines = f.readlines()

new_lines = []
current_buffer = []
found_target = False

# O ID que queremos eliminar
TARGET_PLUGIN = "plugin=ChatAI-Plasmoid"

for line in lines:
    # O arquivo INI do KDE separa seções com colchetes, ex: [Containments][2][Applets][61]
    if line.strip().startswith("["):
        # Se tínhamos uma seção anterior salva no buffer
        if current_buffer:
            # Só salvamos no arquivo final se NÃO achamos o plugin alvo nela
            if not found_target:
                new_lines.extend(current_buffer)
            else:
                print(f"Removendo bloco infectado: {current_buffer[0].strip()}")
        
        # Reinicia o buffer para a nova seção
        current_buffer = [line]
        found_target = False
    else:
        current_buffer.append(line)
        # Verifica se essa linha identifica o plugin inimigo
        if TARGET_PLUGIN in line:
            found_target = True

# Processa o último bloco que ficou no buffer
if current_buffer and not found_target:
    new_lines.extend(current_buffer)
elif current_buffer and found_target:
    print(f"Removendo bloco infectado final: {current_buffer[0].strip()}")

# Reescreve o arquivo
with open(config_path, "w") as f:
    f.writelines(new_lines)

print("Limpeza concluída no arquivo.")
PYTHON_SCRIPT
    
    # Execute the Python removal script
    python3 /tmp/remove_chatai.py
    
    # Clean up
    rm -f /tmp/remove_chatai.py
    
    echo "Uninstalling ChatAI Plasmoid package..."
    
    # Remove the plasmoid package
    kpackagetool6 -t Plasma/Applet -r ChatAI-Plasmoid
    
    # Lock desktop editing mode again
    qdbus6 org.kde.plasmashell /PlasmaShell evaluateScript "lockCorona(true)"
    
    echo "ChatAI Plasmoid removed successfully!"
    echo "You may need to restart Plasma Shell for changes to take full effect."
}

check_chatai() {
    if kpackagetool6 -t Plasma/Applet -l 2>/dev/null | grep -q "ChatAI-Plasmoid"; then
        echo "true"
    else
        echo "false"
    fi
}

case "$ACTION" in
    install)
        install_chatai
        ;;
    remove)
        remove_chatai
        ;;
    check)
        check_chatai
        ;;
    *)
        echo "Usage: $0 {install|remove|check}"
        exit 1
        ;;
esac
