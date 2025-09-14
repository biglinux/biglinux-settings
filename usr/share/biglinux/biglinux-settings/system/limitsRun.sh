#!/bin/bash

#Translation
export TEXTDOMAINDIR="/usr/share/locale"
export TEXTDOMAIN=pipewire-proaudio-config

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

# 1. Creates a named pipe (FIFO) for communication with Zenity
pipePath="/tmp/limits_pipe_$$"
mkfifo "$pipePath"

# 2. Starts Zenity IN THE BACKGROUND, as the user, with the full environment
zenityText=$"Applying, please wait..."
runAsUser "zenity --progress --title='Limits' --text=\"$zenityText\" --pulsate --auto-close --no-cancel < '$pipePath'" &

limitsFinalMessage() {
if [[ "$updateSucesse" == "true" ]]; then
  zenityText=$"Limits updated successfully!"
  runAsUser "zenity --info --text=\"$zenityText\""
else
  zenityText=$"An error occurred while updating Limits."
  runAsUser "zenity --error --text=\"$zenityText\""
fi
}

# 3. Executes the root tasks.
updateLimitsTask() {
  if [[ "$function" == "enable" ]]; then
    # Add the parameter
    echo '@audio - rtprio 90' | tee -a /etc/security/limits.conf
    echo '@audio - memlock unlimited' | tee -a /etc/security/limits.conf
  else
    # remove the parameter
    sed -i -E "/rtprio/d" /etc/security/limits.conf
    sed -i -E "/memlock unlimited/d" /etc/security/limits.conf
  fi
}
updateLimitsTask

# 4. Cleans up the pipe
rm "$pipePath"

# 5. Shows the final result to the user, also with the correct theme.
if [[ "$exitCode" -eq 0 ]]; then
  zenityText=$"Limits updated successfully!"
  runAsUser "zenity --info --text=\"$zenityText\""
else
  zenityText=$"An error occurred while updating Limits."
  runAsUser "zenity --error --text=\"$zenityText\""
fi

# 6. Exits the script with the correct exit code
exit $exitCode
