#!/bin/bash

# check current status
if [ "$1" == "check" ]; then
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    # Verifica se o serviço está habilitado
    what_to_remember=$(kreadconfig6 --file kactivitymanagerd-pluginsrc --group "Plugin-org.kde.ActivityManager.Resources.Scoring" --key "what-to-remember")
    use_recent=$(kreadconfig6 --file kdeglobals --group RecentDocuments --key UseRecent)
    files_enabled=$(kreadconfig6 --file kioslaverc --group "recentlyused" --key "FilesEnabled")

    if [[ "$what_to_remember" == "0" ]] && [[ "${use_recent,,}" == "true" ]] && [[ "${files_enabled,,}" == "true" ]]; then
        echo "true"
    else
        echo "false"
    fi
  elif [[ "$XDG_CURRENT_DESKTOP" == *"GNOME"* ]];then
    remember=$(gsettings get org.gnome.desktop.privacy remember-recent-files 2>/dev/null)
    if [[ "$remember" == "true" ]]; then
      echo "true"
    else
      echo "false"
    fi
  elif [[ "$XDG_CURRENT_DESKTOP" == *"XFCE"* ]];then
    recent_enabled=$(xfconf-query -c xfce4-session -p /general/SaveOnExit 2>/dev/null)
    if [[ "$recent_enabled" == "true" ]]; then
      echo "true"
    else
      echo "false"
    fi
  elif [[ "$XDG_CURRENT_DESKTOP" == *"Cinnamon"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"X-Cinnamon"* ]];then
    recent_status=$(gsettings get org.cinnamon.desktop.privacy remember-recent-files)
    if [[ "$recent_status" == "true" ]]; then
      echo "true"
    else
      echo "false"
    fi
  fi

# change the state
elif [ "$1" == "toggle" ]; then
  state="$2"
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    if [ "$state" == "true" ]; then
      $PWD/usability/recentFilesRun.sh "enable"
      exitCode=$?
    else
      $PWD/usability/recentFilesRun.sh "disable"
      exitCode=$?
    fi
  elif [[ "$XDG_CURRENT_DESKTOP" == *"GNOME"* ]];then
    if [ "$state" == "true" ]; then
        gsettings set org.gnome.desktop.privacy remember-recent-files true
        exitCode=$?
    else
        gsettings set org.gnome.desktop.privacy remember-recent-files false
        exitCode=$?
    fi
  elif [[ "$XDG_CURRENT_DESKTOP" == *"XFCE"* ]];then
    if [ "$state" == "true" ]; then
        xfconf-query -c xfce4-session -p /general/SaveOnExit -s true 2>/dev/null
        exitCode=$?
    else
        xfconf-query -c xfce4-session -p /general/SaveOnExit -s false 2>/dev/null
        exitCode=$?
    fi
  elif [[ "$XDG_CURRENT_DESKTOP" == *"Cinnamon"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"X-Cinnamon"* ]];then
    if [ "$state" == "true" ]; then
        gsettings set org.cinnamon.desktop.privacy remember-recent-files true
        exitCode=$?
    else
        gsettings set org.cinnamon.desktop.privacy remember-recent-files false
        exitCode=$?
    fi
  fi
  exit $exitCode
fi
