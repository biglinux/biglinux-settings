#!/bin/bash
# KDE Recent Files & Locations Fix
# Autor: Rafael Ruscher
# Script para biglinux-settings

ACTION="$1"

# Detecta versão do Plasma
if command -v balooctl6 &>/dev/null; then
    BALOOCMD="balooctl6"
    KCMD="kwriteconfig6"
else
    BALOOCMD="balooctl"
    KCMD="kwriteconfig5"
fi

# Arquivos de configuração
ACTIVITY_RC="$HOME/.config/kactivitymanagerd-pluginsrc"
KDEGLOBALS_RC="$HOME/.config/kdeglobals"
KIOSLAVE_RC="$HOME/.config/kioslaverc"
XBEL_FILE="$HOME/.local/share/recently-used.xbel"
ACTIVITY_DB_DIR="$HOME/.local/share/kactivitymanagerd/resources"

check_status() {
    # Verifica se o serviço está habilitado
    local what_to_remember
    what_to_remember=$(kreadconfig5 --file kactivitymanagerd-pluginsrc \
        --group "Plugin-org.kde.ActivityManager.Resources.Scoring" \
        --key "what-to-remember" 2>/dev/null || \
        kreadconfig6 --file kactivitymanagerd-pluginsrc \
        --group "Plugin-org.kde.ActivityManager.Resources.Scoring" \
        --key "what-to-remember" 2>/dev/null)
    
    local use_recent
    use_recent=$(kreadconfig5 --file kdeglobals --group RecentDocuments --key UseRecent 2>/dev/null || \
                 kreadconfig6 --file kdeglobals --group RecentDocuments --key UseRecent 2>/dev/null)
    
    local files_enabled
    files_enabled=$(kreadconfig5 --file kioslaverc --group "recentlyused" --key "FilesEnabled" 2>/dev/null || \
                    kreadconfig6 --file kioslaverc --group "recentlyused" --key "FilesEnabled" 2>/dev/null)
    
    # Se what-to-remember é 0 (lembrar tudo) e UseRecent é true e FilesEnabled é true = ativado
    if [[ "$what_to_remember" == "0" ]] && [[ "${use_recent,,}" == "true" ]] && [[ "${files_enabled,,}" == "true" ]]; then
        echo "true"
    else
        echo "false"
    fi
}

enable_recent_files() {
    echo "STATUS:Stopping services..."
    echo "PROGRESS:5"
    
    # Para serviços
    $BALOOCMD suspend 2>/dev/null
    $BALOOCMD disable 2>/dev/null
    killall baloo_file dolphin kactivitymanagerd kioworker kiod5 kiod6 2>/dev/null
    systemctl --user stop plasma-kactivitymanagerd.service 2>/dev/null
    
    echo "STATUS:Removing off-the-record lock..."
    echo "PROGRESS:15"
    
    # Remove trava off-the-record
    sed -i '/off-the-record-activities/d' "$ACTIVITY_RC" 2>/dev/null
    
    echo "STATUS:Configuring activity tracking..."
    echo "PROGRESS:25"
    
    # Configura rastreamento de atividades
    $KCMD --file kactivitymanagerd-pluginsrc \
        --group "Plugin-org.kde.ActivityManager.Resources.Scoring" \
        --key "what-to-remember" "0"
    $KCMD --file kactivitymanagerd-pluginsrc \
        --group "Plugin-org.kde.ActivityManager.Resources.Scoring" \
        --key "enabled" "true"
    
    echo "STATUS:Configuring recent documents..."
    echo "PROGRESS:40"
    
    # Configura documentos recentes
    $KCMD --file kdeglobals --group RecentDocuments --key UseRecent true
    $KCMD --file kdeglobals --group RecentDocuments --key MaxEntries 50
    
    echo "STATUS:Configuring KIO slave..."
    echo "PROGRESS:55"
    
    # Configura kioslave para arquivos recentes
    $KCMD --file kioslaverc --group "recentlyused" --key "MaxItems" "100"
    $KCMD --file kioslaverc --group "recentlyused" --key "LocationsEnabled" "true"
    $KCMD --file kioslaverc --group "recentlyused" --key "FilesEnabled" "true"
    
    echo "STATUS:Recreating database..."
    echo "PROGRESS:65"
    
    # Limpa e recria banco de dados
    rm -rf "$ACTIVITY_DB_DIR"
    mkdir -p "$ACTIVITY_DB_DIR"
    
    echo "STATUS:Creating recently-used.xbel..."
    echo "PROGRESS:75"
    
    # Recria recently-used.xbel
    [ -f "$XBEL_FILE" ] && cp "$XBEL_FILE" "$XBEL_FILE.bak"
    cat > "$XBEL_FILE" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<xbel version="1.0"
      xmlns:bookmark="http://www.freedesktop.org/standards/desktop-bookmarks"
      xmlns:mime="http://www.freedesktop.org/standards/shared-mime-info">
</xbel>
EOF
    chmod 644 "$XBEL_FILE"
    
    echo "STATUS:Starting services..."
    echo "PROGRESS:85"
    
    # Reinicia serviços
    systemctl --user start plasma-kactivitymanagerd.service
    sleep 2
    
    $BALOOCMD enable 2>/dev/null
    $BALOOCMD resume 2>/dev/null
    
    echo "STATUS:Restarting activity manager..."
    echo "PROGRESS:95"
    
    systemctl --user restart plasma-kactivitymanagerd.service
    killall kiod5 kiod6 2>/dev/null
    
    sleep 1
    
    echo "STATUS:Completed successfully!"
    echo "PROGRESS:100"
    echo "RESULT:success"
}

disable_recent_files() {
    echo "STATUS:Stopping services..."
    echo "PROGRESS:5"
    
    # Para serviços
    killall dolphin kactivitymanagerd kioworker kiod5 kiod6 2>/dev/null
    systemctl --user stop plasma-kactivitymanagerd.service 2>/dev/null
    
    echo "STATUS:Disabling activity tracking..."
    echo "PROGRESS:20"
    
    # Desabilita rastreamento de atividades
    $KCMD --file kactivitymanagerd-pluginsrc \
        --group "Plugin-org.kde.ActivityManager.Resources.Scoring" \
        --key "what-to-remember" "2"  # 2 = não lembrar nada
    $KCMD --file kactivitymanagerd-pluginsrc \
        --group "Plugin-org.kde.ActivityManager.Resources.Scoring" \
        --key "enabled" "false"
    
    echo "STATUS:Disabling recent documents..."
    echo "PROGRESS:40"
    
    # Desabilita documentos recentes
    $KCMD --file kdeglobals --group RecentDocuments --key UseRecent false
    
    echo "STATUS:Disabling KIO slave recent files..."
    echo "PROGRESS:55"
    
    # Desabilita kioslave para arquivos recentes
    $KCMD --file kioslaverc --group "recentlyused" --key "LocationsEnabled" "false"
    $KCMD --file kioslaverc --group "recentlyused" --key "FilesEnabled" "false"
    
    echo "STATUS:Clearing database..."
    echo "PROGRESS:70"
    
    # Limpa banco de dados
    rm -rf "$ACTIVITY_DB_DIR"
    
    echo "STATUS:Clearing recently-used.xbel..."
    echo "PROGRESS:80"
    
    # Limpa recently-used.xbel
    cat > "$XBEL_FILE" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<xbel version="1.0"
      xmlns:bookmark="http://www.freedesktop.org/standards/desktop-bookmarks"
      xmlns:mime="http://www.freedesktop.org/standards/shared-mime-info">
</xbel>
EOF
    chmod 644 "$XBEL_FILE"
    
    echo "STATUS:Restarting services..."
    echo "PROGRESS:90"
    
    # Reinicia serviços
    systemctl --user start plasma-kactivitymanagerd.service
    killall kiod5 kiod6 2>/dev/null
    
    sleep 1
    
    echo "STATUS:Completed successfully!"
    echo "PROGRESS:100"
    echo "RESULT:success"
}

# Main
case "$ACTION" in
    check)
        check_status
        ;;
    toggle)
        TOGGLE_STATE="$2"
        if [[ "$TOGGLE_STATE" == "true" ]]; then
            enable_recent_files
        else
            disable_recent_files
        fi
        ;;
    enable_gui)
        enable_recent_files
        ;;
    disable_gui)
        disable_recent_files
        ;;
    *)
        echo "Usage: $0 {check|toggle true|toggle false|enable_gui|disable_gui}"
        exit 1
        ;;
esac

exit 0
