#!/bin/bash

#Translation
export TEXTDOMAINDIR="/usr/share/locale"
export TEXTDOMAIN=biglinux-settings

# Assign the received arguments to variables with clear names
timeout="$1"
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

# 1. Creates a named pipe (FIFO) for communication with Zenity
pipePath="/tmp/grub_pipe_$$"
mkfifo "$pipePath"

# 2. Starts Zenity IN THE BACKGROUND, as the user, with the full environment
runAsUser "zenity --progress --title='grub' --text=$\"Applying, please wait...\" --pulsate --auto-close < '$pipePath'" &

# 3. Executes the root tasks.
updateGrubTask() {
    sed -i "/GRUB_TIMEOUT=/s/=.*/=$timeout/" /etc/default/grub
    update-grub > "$pipePath"
}
updateGrubTask
exitCode=$?

# 4. Cleans up the pipe
rm "$pipePath"

# 5. Shows the final result to the user, also with the correct theme.
if [[ "$exitCode" -eq 0 ]]; then
  runAsUser "zenity --info --text=$\"GRUB updated successfully!\""
else
  runAsUser "zenity --error --text=$\"An error occurred while updating GRUB.\""
fi

# 6. Exits the script with the correct exit code
exit $exitCode
