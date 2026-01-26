#!/bin/bash

#Translation
export TEXTDOMAINDIR="/usr/share/locale"
export TEXTDOMAIN=biglinux-settings

# Assign the received arguments to variables with clear names
function="$1"
package="$2"
originalUser="$3"
userDisplay="$4"
userXauthority="$5"
userDbusAddress="$6"
userLang="$7"
userLanguage="$8"

# Helper function to run a command as the original user
runAsUser() {
  # Single quotes around variables are a good security practice
  su "$originalUser" -c "export DISPLAY='$userDisplay'; export XAUTHORITY='$userXauthority'; export DBUS_SESSION_BUS_ADDRESS='$userDbusAddress'; export LANG='$userLang'; export LC_ALL='$userLang'; export LANGUAGE='$userLanguage'; $1"
}

# 1. Creates a named pipe (FIFO) for communication with Zenity
pipePath="/tmp/container_manager_pipe_$$"
mkfifo "$pipePath"

# 2. Starts Zenity IN THE BACKGROUND, as the user
if [[ "$function" == "install" ]]; then
  zenityTitle=$"Installing $package"
  zenityText=$"Installing $package, Please wait..."
elif [[ "$function" == "remove" ]]; then
  zenityTitle=$"Removing $package"
  zenityText=$"Removing $package, Please wait..."
fi
runAsUser "zenity --progress --title=\"$zenityTitle\" --text=\"$zenityText\" --pulsate --auto-close --no-cancel < '$pipePath'" &

# 3. Executes the root tasks.
managePackage() {
  if [[ "$function" == "install" ]]; then
    # Update database and install
    pacman -Syu --noconfirm "$package"
  elif [[ "$function" == "remove" ]]; then
    # Remove package
    pacman -Rcs --noconfirm "$package"
  fi
  exitCode=$?
}
managePackage > "$pipePath"

# 4. Cleans up the pipe
rm "$pipePath"

# 5. Shows the final result
if [[ "$exitCode" == "0" ]]; then
  if [[ "$function" == "install" ]]; then
      zenityText=$"$package installed successfully!"
  else
      zenityText=$"$package removed successfully!"
  fi
  runAsUser "zenity --info --text=\"$zenityText\""
else
  zenityText=$"An error occurred with $package."
  runAsUser "zenity --error --text=\"$zenityText\""
fi

# 6. Exits the script
exit $exitCode
