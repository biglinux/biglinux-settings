#!/bin/bash

# Arquivos de configuração
BALOOCMD="balooctl6"
KCMD="kwriteconfig6"
ACTIVITY_RC="$HOME/.config/kactivitymanagerd-pluginsrc"
KDEGLOBALS_RC="$HOME/.config/kdeglobals"
KIOSLAVE_RC="$HOME/.config/kioslaverc"
XBEL_FILE="$HOME/.local/share/recently-used.xbel"
ACTIVITY_DB_DIR="$HOME/.local/share/kactivitymanagerd/resources"

# check current status
check_state() {
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    # Verifica se o serviço está habilitado
    local what_to_remember
    what_to_remember=$(kreadconfig6 --file kactivitymanagerd-pluginsrc --group "Plugin-org.kde.ActivityManager.Resources.Scoring" --key "what-to-remember")

    local use_recent
    use_recent=$(kreadconfig6 --file kdeglobals --group RecentDocuments --key UseRecent)

    local files_enabled
    files_enabled=$(kreadconfig6 --file kioslaverc --group "recentlyused" --key "FilesEnabled")

    # Se what-to-remember é 0 (lembrar tudo) e UseRecent é true e FilesEnabled é true = ativado
    if [[ "$what_to_remember" == "0" ]] && [[ "${use_recent,,}" == "true" ]] && [[ "${files_enabled,,}" == "true" ]]; then
        echo "true"
    else
        echo "false"
    fi
#   elif [[ "$XDG_CURRENT_DESKTOP" == *"GNOME"* ]];then
#     if [[ "$someTest" == "true" ]];then
#       echo "true"
#     else
#       echo "false"
#     fi
#   elif [[ "$XDG_CURRENT_DESKTOP" == *"XFCE"* ]];then
#     if [[ "$someTest" == "true" ]];then
#       echo "true"
#     else
#       echo "false"
#     fi
#   elif [[ "$XDG_CURRENT_DESKTOP" == *"Cinnamon"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"X-Cinnamon"* ]];then
#     if [[ "$someTest" == "true" ]];then
#       echo "true"
#     else
#       echo "false"
#     fi
  fi
}

# change the state
toggle_state() {
  new_state="$1"
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    if [[ "$new_state" == "true" ]];then
      # Para serviços
      $BALOOCMD suspend
      $BALOOCMD disable
      killall baloo_file dolphin kactivitymanagerd kioworker kiod5 kiod6
      systemctl --user stop plasma-kactivitymanagerd.service

      # Remove trava off-the-record
      sed -i '/off-the-record-activities/d' "$ACTIVITY_RC"

      # Configura rastreamento de atividades
      $KCMD --file kactivitymanagerd-pluginsrc --group "Plugin-org.kde.ActivityManager.Resources.Scoring" --key "what-to-remember" "0"
      $KCMD --file kactivitymanagerd-pluginsrc --group "Plugin-org.kde.ActivityManager.Resources.Scoring" --key "enabled" "true"

      # Configura documentos recentes
      $KCMD --file kdeglobals --group RecentDocuments --key UseRecent true
      $KCMD --file kdeglobals --group RecentDocuments --key MaxEntries 50

      # Configura kioslave para arquivos recentes
      $KCMD --file kioslaverc --group "recentlyused" --key "MaxItems" "100"
      $KCMD --file kioslaverc --group "recentlyused" --key "LocationsEnabled" "true"
      $KCMD --file kioslaverc --group "recentlyused" --key "FilesEnabled" "true"

      # Limpa e recria banco de dados
      rm -rf "$ACTIVITY_DB_DIR"
      mkdir -p "$ACTIVITY_DB_DIR"

      # Recria recently-used.xbel
      [ -f "$XBEL_FILE" ] && cp "$XBEL_FILE" "$XBEL_FILE.bak"
      echo '<?xml version="1.0" encoding="UTF-8"?>
<xbel version="1.0"
    xmlns:bookmark="http://www.freedesktop.org/standards/desktop-bookmarks"
    xmlns:mime="http://www.freedesktop.org/standards/shared-mime-info">
</xbel>' > "$XBEL_FILE"

      chmod 644 "$XBEL_FILE"

      # Reinicia serviços
      systemctl --user start plasma-kactivitymanagerd.service
      sleep 2

      $BALOOCMD enable
      $BALOOCMD resume

      systemctl --user restart plasma-kactivitymanagerd.service
      killall kiod5 kiod6

      sleep 1

      echo "STATUS:Completed successfully!"
      echo "PROGRESS:100"
      echo "RESULT:success"
      exit=$?
    else
      # Para serviços
      killall dolphin kactivitymanagerd kioworker kiod5 kiod6
      systemctl --user stop plasma-kactivitymanagerd.service

      # Desabilita rastreamento de atividades
      $KCMD --file kactivitymanagerd-pluginsrc --group "Plugin-org.kde.ActivityManager.Resources.Scoring" --key "what-to-remember" "2"
      $KCMD --file kactivitymanagerd-pluginsrc --group "Plugin-org.kde.ActivityManager.Resources.Scoring" --key "enabled" "false"

      # Desabilita documentos recentes
      $KCMD --file kdeglobals --group RecentDocuments --key UseRecent false

      # Desabilita kioslave para arquivos recentes
      $KCMD --file kioslaverc --group "recentlyused" --key "LocationsEnabled" "false"
      $KCMD --file kioslaverc --group "recentlyused" --key "FilesEnabled" "false"

      # Limpa banco de dados
      rm -rf "$ACTIVITY_DB_DIR"

      # Limpa recently-used.xbel
  echo '<?xml version="1.0" encoding="UTF-8"?>
<xbel version="1.0"
      xmlns:bookmark="http://www.freedesktop.org/standards/desktop-bookmarks"
      xmlns:mime="http://www.freedesktop.org/standards/shared-mime-info">
</xbel>' > "$XBEL_FILE"

      chmod 644 "$XBEL_FILE"

      # Reinicia serviços
      systemctl --user start plasma-kactivitymanagerd.service
      killall kiod5 kiod6

      sleep 1

      return $?
    fi
#   elif [[ "$XDG_CURRENT_DESKTOP" == *"GNOME"* ]];then
#     if [[ "$new_state" == "true" ]];then
#         some command
#         exitCode=$?
#     else
#         some command
#         exitCode=$?
#     fi
#   elif [[ "$XDG_CURRENT_DESKTOP" == *"XFCE"* ]];then
#     if [[ "$new_state" == "true" ]];then
#         some command
#         exitCode=$?
#     else
#         some command
#         exitCode=$?
#     fi
#   elif [[ "$XDG_CURRENT_DESKTOP" == *"Cinnamon"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"X-Cinnamon"* ]];then
#     if [[ "$new_state" == "true" ]];then
#         some command
#         exitCode=$?
#     else
#         some command
#         exitCode=$?
#     fi
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
