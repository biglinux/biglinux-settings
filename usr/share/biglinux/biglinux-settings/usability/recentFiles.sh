#!/bin/bash

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
      $PWD/usability/recentFilesRun.sh "enable" #"$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
      exit=$?
    else
      $PWD/usability/recentFilesRun.sh "disable" #"$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
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
