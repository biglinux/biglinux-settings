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
parameter='mitigations=off'

# Helper function to run a command as the original user
runAsUser() {
  # Single quotes around variables are a good security practice
  su "$originalUser" -c "export DISPLAY='$userDisplay'; export XAUTHORITY='$userXauthority'; export DBUS_SESSION_BUS_ADDRESS='$userDbusAddress'; export LANG='$userLang'; export LC_ALL='$userLang'; export LANGUAGE='$userLanguage'; $1"
}

# 1. Creates a named pipe (FIFO) for communication with Zenity
pipePath="/tmp/grub_pipe_$$"
mkfifo "$pipePath"

# 2. Starts Zenity IN THE BACKGROUND, as the user, with the full environment
zenityText=$"Applying, please wait..."
runAsUser "zenity --progress --title='grub' --text=\"$zenityText\" --pulsate --auto-close --no-cancel < '$pipePath'" &

grubFinalMessage() {
if [[ "$updateSucesse" == "true" ]]; then
  zenityText=$"GRUB updated successfully!\nRestart your computer for it to take effect."
  runAsUser "zenity --info --text=\"$zenityText\""
else
  zenityText=$"An error occurred while updating GRUB."
  runAsUser "zenity --error --text=\"$zenityText\""
fi
}

# 3. Executes the root tasks.
updateGrubTask() {
  if [[ "$function" == "enable" ]]; then
    if grep -q "$parameter" "/etc/default/grub"; then
      # Already enabled, nothing to do. Inform zenity and exit the function gracefully.
      echo $"Already disabled. No changes made." > "$pipePath"
      return
    elif grep -q "GRUB_CMDLINE_LINUX_DEFAULT=" "/etc/default/grub"; then
      # Add the parameter
      sed -i.bak -E "/^GRUB_CMDLINE_LINUX_DEFAULT=/ s|(['\"])$| $parameter\1|" "/etc/default/grub"
    elif grep -q "GRUB_CMDLINE_LINUX=" "/etc/default/grub"; then
      # Add the parameter
      sed -i.bak -E "/^GRUB_CMDLINE_LINUX=/ s|(['\"])$| $parameter\1|" "/etc/default/grub"
    fi
  else
    # remove the parameter
    sed -i -E "s/$parameter//g" "/etc/default/grub"
  fi

  # Run update-grub only if changes were made
  # some systems do not have update-grub and grub-mkconfig in the path, so check the file directly.
  if [[ -e "/usr/bin/update-grub" ]];then
    /usr/bin/update-grub > "$pipePath"
  elif [[ -e "/usr/sbin/update-grub" ]];then
    /usr/sbin/update-grub > "$pipePath"
  elif [[ -e "/usr/bin/grub-mkconfig" ]];then
    /usr/bin/grub-mkconfig > "$pipePath"
  elif [[ -e "/usr/sbin/grub-mkconfig" ]];then
    /usr/sbin/grub-mkconfig > "$pipePath"
  elif [[ -e "/usr/bin/grub2-mkconfig" ]];then
    /usr/bin/grub2-mkconfig > "$pipePath"
  elif [[ -e "/usr/sbin/grub2-mkconfig" ]];then
    /usr/sbin/grub2-mkconfig > "$pipePath"
  fi
  exitCode=$?
}
updateGrubTask

# 4. Cleans up the pipe
rm "$pipePath"

# 5. Shows the final result to the user, also with the correct theme.
if [[ "$exitCode" -eq 0 ]]; then
  zenityText=$"GRUB updated successfully!\nRestart your computer for it to take effect."
  runAsUser "zenity --info --text=\"$zenityText\""
else
  zenityText=$"An error occurred while updating GRUB."
  runAsUser "zenity --error --text=\"$zenityText\""
fi

# 6. Exits the script with the correct exit code
exit $exitCode
