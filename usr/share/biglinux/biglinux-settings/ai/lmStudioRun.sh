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

# Helper function to run a command as the original user
runAsUser() {
  # Single quotes around variables are a good security practice
  su "$originalUser" -c "export DISPLAY='$userDisplay'; export XAUTHORITY='$userXauthority'; export DBUS_SESSION_BUS_ADDRESS='$userDbusAddress'; export LANG='$userLang'; export LC_ALL='$userLang'; export LANGUAGE='$userLanguage'; $1"
}

# Creates a named pipe (FIFO) for communication with Zenity
pipePath="/tmp/lmStudio_pipe_$$"
mkfifo "$pipePath"

# Starts Zenity IN THE BACKGROUND, as the user, with the full environment
if [[ "$function" == "install" ]]; then
  zenityTitle=$"LM Studio Install"
  zenityText=$"Instaling LM Studio, Please wait..."
fi
runAsUser "zenity --progress --title=\"$zenityTitle\" --text=\"$zenityText\" --pulsate --auto-close --no-cancel < '$pipePath'" &

# Executes the root tasks.
updateTask() {
  if [[ "$function" == "install" ]]; then
    pacman -Syu --noconfirm lmstudio-bin
  else
    pacman -Rcs --noconfirm lmstudio-bin
  fi
  exitCode=$?
}
updateTask > "$pipePath"

# Cleans up the pipe
rm "$pipePath"

# Shows the final result to the user, also with the correct theme.
if [[ "$exitCode" == "0" ]] && [[ "$function" == "install" ]]; then
  zenityText=$"LM Studio installed successfully!"
  runAsUser "zenity --info --text=\"$zenityText\""
else
  zenityText=$"Failed to install LM Studio!"
  zenity --info --text="$zenityText"
fi

# Exits the script with the correct exit code
exit $exitCode
