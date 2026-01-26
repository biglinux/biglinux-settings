#!/bin/bash

#Translation
export TEXTDOMAINDIR="/usr/share/locale"
export TEXTDOMAIN=biglinux-settings

# Assign the received arguments to variables with clear names
function="$1"
originalUser="$2"
userDisplay="$3"
userXauthority="$4"
userDbusAddress="$5"
userLang="$6"
userLanguage="$7"

# Configuration commands
balooCMD="balooctl6"
kwriteConfig="kwriteconfig6"

# Configuration files
xbelFile="$HOME/.local/share/recently-used.xbel"
kactivitymanagerdFile="$HOME/.config/kactivitymanagerd-pluginsrc"
kactivitymanagerdDir="$HOME/.local/share/kactivitymanagerd/resources"

# Helper function to run a command as the original user
runAsUser() {
  # Single quotes around variables are a good security practice
  su "$originalUser" -c "export DISPLAY='$userDisplay'; export XAUTHORITY='$userXauthority'; export DBUS_SESSION_BUS_ADDRESS='$userDbusAddress'; export LANG='$userLang'; export LC_ALL='$userLang'; export LANGUAGE='$userLanguage'; $1"
}

# Creates a named pipe (FIFO) for communication with Zenity
pipePath="/tmp/recentfiles_pipe_$$"
mkfifo "$pipePath"

# Starts Zenity IN THE BACKGROUND, as the user, with the full environment
if [[ "$function" == "enable" ]]; then
  zenityTitle=$"Recent Files enabling...."
  zenityText=$"Recent Files enabling, Please wait..."
fi
runAsUser "zenity --progress --title=\"$zenityTitle\" --text=\"$zenityText\" --pulsate --auto-close --no-cancel < '$pipePath'" &

# Executes the root tasks.
updateTask() {
  if [[ "$function" == "enable" ]]; then
    $balooCMD suspend
    $balooCMD disable
    killall baloo_file dolphin kactivitymanagerd kioworker kiod5 kiod6
    systemctl --user stop plasma-kactivitymanagerd.service

    # Remove trava off-the-record
    sed -i '/off-the-record-activities/d' "$kactivitymanagerdFile"

    # Configura rastreamento de atividades
    $kwriteConfig --file kactivitymanagerd-pluginsrc --group "Plugin-org.kde.ActivityManager.Resources.Scoring" --key "what-to-remember" "0"
    $kwriteConfig --file kactivitymanagerd-pluginsrc --group "Plugin-org.kde.ActivityManager.Resources.Scoring" --key "enabled" "true"

    # Configura documentos recentes
    $kwriteConfig --file kdeglobals --group RecentDocuments --key UseRecent true
    $kwriteConfig --file kdeglobals --group RecentDocuments --key MaxEntries 50

    # Configura kioslave para arquivos recentes
    $kwriteConfig --file kioslaverc --group "recentlyused" --key "MaxItems" "100"
    $kwriteConfig --file kioslaverc --group "recentlyused" --key "LocationsEnabled" "true"
    $kwriteConfig --file kioslaverc --group "recentlyused" --key "FilesEnabled" "true"

    # Limpa e recria banco de dados
    rm -rf "$kactivitymanagerdDir"
    mkdir -p "$kactivitymanagerdDir"

    # Recria recently-used.xbel
    [ -f "$xbelFile" ] && cp "$xbelFile" "$xbelFile.bak"
    echo '<?xml version="1.0" encoding="UTF-8"?>
  <xbel version="1.0"
  xmlns:bookmark="http://www.freedesktop.org/standards/desktop-bookmarks"
  xmlns:mime="http://www.freedesktop.org/standards/shared-mime-info">
  </xbel>' > "$xbelFile"

    chmod 644 "$xbelFile"

    # Reinicia serviços
    systemctl --user start plasma-kactivitymanagerd.service
    sleep 2

    $balooCMD enable
    $balooCMD resume

    systemctl --user restart plasma-kactivitymanagerd.service
    killall kiod5 kiod6

    sleep 1

    echo "STATUS:Completed successfully!"
    echo "PROGRESS:100"
    echo "RESULT:success"
  else
    # Para serviços
    killall dolphin kactivitymanagerd kioworker kiod5 kiod6
    systemctl --user stop plasma-kactivitymanagerd.service

    # Desabilita rastreamento de atividades
    $kwriteConfig --file kactivitymanagerd-pluginsrc --group "Plugin-org.kde.ActivityManager.Resources.Scoring" --key "what-to-remember" "2"
    $kwriteConfig --file kactivitymanagerd-pluginsrc --group "Plugin-org.kde.ActivityManager.Resources.Scoring" --key "enabled" "false"

    # Desabilita documentos recentes
    $kwriteConfig --file kdeglobals --group RecentDocuments --key UseRecent false

    # Desabilita kioslave para arquivos recentes
    $kwriteConfig --file kioslaverc --group "recentlyused" --key "LocationsEnabled" "false"
    $kwriteConfig --file kioslaverc --group "recentlyused" --key "FilesEnabled" "false"

    # Limpa banco de dados
    rm -rf "$kactivitymanagerdDir"

    # Limpa recently-used.xbel
    echo '<?xml version="1.0" encoding="UTF-8"?>
  <xbel version="1.0"
    xmlns:bookmark="http://www.freedesktop.org/standards/desktop-bookmarks"
    xmlns:mime="http://www.freedesktop.org/standards/shared-mime-info">
  </xbel>' > "$xbelFile"

    chmod 644 "$xbelFile"

    # Reinicia serviços
    systemctl --user start plasma-kactivitymanagerd.service
    killall kiod5 kiod6

    sleep 1
  fi
  exitCode=$?
}
updateTask > "$pipePath"

# Cleans up the pipe
rm "$pipePath"

# Shows the final result to the user, also with the correct theme.
if [[ "$exitCode" == "0" ]] && [[ "$function" == "enable" ]]; then
  zenityText=$"Recent Files successfully enabled!"
  runAsUser "zenity --info --text=\"$zenityText\""
elif [[ "$exitCode" == "0" ]] && [[ "$function" == "disable" ]]; then
  zenityText=$"Recent Files successfully disable!"
  runAsUser "zenity --info --text=\"$zenityText\""
else
  zenityText=$"Failed to activate Recent Files!"
  runAsUser "zenity --info --text=\"$zenityText\""
fi

# Exits the script with the correct exit code
exit $exitCode
