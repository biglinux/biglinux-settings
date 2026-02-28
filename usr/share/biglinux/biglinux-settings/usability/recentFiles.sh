#!/bin/bash

# check current status
# action=$1
if [ "$1" == "check" ]; then
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
  elif [[ "$XDG_CURRENT_DESKTOP" == *"Cinnamon"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"X-Cinnamon"* ]];then
    recent_status=$(gsettings get org.cinnamon.desktop.privacy remember-recent-files)
    if [[ "$recent_status" == "true" ]]; then
      echo "true"
    else
      echo "false"
    fi
  fi

# change the state
# action=$1
# state=$2
elif [ "$1" == "toggle" ]; then
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    if [ "$2" == "true" ]; then
      $PWD/usability/recentFilesRun.sh "enable" #"$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    else
      $PWD/usability/recentFilesRun.sh "disable" #"$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    fi
#   elif [[ "$XDG_CURRENT_DESKTOP" == *"GNOME"* ]];then
#     if [ "$2" == "true" ]; then
#         some command
#         exitCode=$?
#     else
#         some command
#         exitCode=$?
#     fi
#   elif [[ "$XDG_CURRENT_DESKTOP" == *"XFCE"* ]];then
#     if [ "$2" == "true" ]; then
#         some command
#     else
#         some command
#     fi
  elif [[ "$XDG_CURRENT_DESKTOP" == *"Cinnamon"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"X-Cinnamon"* ]];then
    if [ "$2" == "true" ]; then
	      gsettings set org.cinnamon.desktop.privacy remember-recent-files true
    else
        gsettings set org.cinnamon.desktop.privacy remember-recent-files false
    fi
  fi
  exit $?
fi
