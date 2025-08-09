#!/bin/bash

# Script para gerenciar tema escuro
# Funções: check_state e toggle_state

check_state() {
    # Função para verificar estado atual
    local current_theme=$(gsettings get org.gnome.desktop.interface gtk-theme 2>/dev/null)

    if [[ "$current_theme" == *"dark"* ]]; then
        echo "true"
        return 0
    else
        echo "false"
        return 1
    fi
}

toggle_state() {
    # Função para alterar o estado
    local new_state="$1"

    if [[ "$new_state" == "true" ]]; then
        echo "Ativando tema escuro..."
        gsettings set org.gnome.desktop.interface gtk-theme 'Adwaita-dark'
        return 0
    else
        echo "Ativando tema claro..."
        gsettings set org.gnome.desktop.interface gtk-theme 'Adwaita'
        return 0
    fi
}

# Executa a função baseada no parâmetro
case "$1" in
    "check")
        check_state
        ;;
    "toggle")
        toggle_state "$2"
        ;;
    *)
        echo "Uso: $0 {check|toggle} [true|false]"
        echo "  check          - Verifica estado atual"
        echo "  toggle <state> - Altera para o estado especificado"
        exit 1
        ;;
esac
