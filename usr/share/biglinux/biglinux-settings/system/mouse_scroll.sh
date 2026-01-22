#!/bin/bash
# Mouse Scroll Invert - BigLinux Settings
# Inverte a rolagem do mouse sem precisar reiniciar a sessão

ACTION="${1:-toggle}"
CONFIG_FILE="$HOME/.config/kcminputrc"

# Função para verificar o estado atual
check_state() {
    CURRENT_CFG=$(kreadconfig6 --file "$CONFIG_FILE" --group "Mouse" --key "NaturalScroll" 2>/dev/null)
    if [ "$CURRENT_CFG" == "true" ]; then
        echo "true"
    else
        echo "false"
    fi
}

# Função para aplicar configuração em tempo real via D-Bus
apply_live() {
    local NEW_STATE="$1"
    
    # Detecta o comando qdbus correto
    if command -v qdbus6 &> /dev/null; then
        QDBUS="qdbus6"
    else
        QDBUS="qdbus"
    fi
    
    # Pega todos os dispositivos de entrada
    DEVICES=$($QDBUS org.kde.KWin 2>/dev/null | grep "/org/kde/KWin/InputDevice/event")
    
    # Força o novo estado em TODOS os dispositivos encontrados
    for DEV in $DEVICES; do
        $QDBUS org.kde.KWin "$DEV" org.kde.KWin.InputDevice.naturalScroll "$NEW_STATE" &> /dev/null
    done
}

# Função para ativar (Natural Scroll)
enable_scroll() {
    # Atualiza o arquivo de configuração
    kwriteconfig6 --file "$CONFIG_FILE" --group "Mouse" --key "NaturalScroll" "true"
    
    # Aplica em tempo real
    apply_live "true"
    
    # Notificação
    notify-send "Mouse Config" "Scroll Invertido: ATIVADO (Natural)" --icon="input-tablet" --urgency=low
    
    echo "enabled"
}

# Função para desativar (Default Scroll)
disable_scroll() {
    # Atualiza o arquivo de configuração
    kwriteconfig6 --file "$CONFIG_FILE" --group "Mouse" --key "NaturalScroll" "false"
    
    # Aplica em tempo real
    apply_live "false"
    
    # Notificação
    notify-send "Mouse Config" "Scroll Invertido: DESATIVADO (Padrão)" --icon="input-mouse" --urgency=low
    
    echo "disabled"
}

# Função para alternar
toggle_scroll() {
    CURRENT_STATE=$(check_state)
    
    if [ "$CURRENT_STATE" == "true" ]; then
        disable_scroll
    else
        enable_scroll
    fi
}

# Processamento de ações
case "$ACTION" in
    "check")
        # Retorna o estado atual para sincronização do switch
        check_state
        ;;
    "enable")
        enable_scroll
        ;;
    "disable")
        disable_scroll
        ;;
    "toggle")
        toggle_scroll
        ;;
    *)
        echo "Usage: $0 {check|enable|disable|toggle}"
        exit 1
        ;;
esac
