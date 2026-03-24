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

# 1. Creates a named pipe (FIFO) for communication with Zenity
pipePath="/tmp/docker_pipe_$$"
mkfifo "$pipePath"

# 2. Starts Zenity IN THE BACKGROUND, as the user, with the full environment
if [[ "$function" == "install" ]]; then
  zenityTitle=$"Docker Install"
  zenityText=$"Installing Docker, Please wait..."
elif [[ "$function" == "enable" ]]; then
  zenityTitle=$"Docker Start"
  zenityText=$"Docker Starting, Please wait..."
elif [[ "$function" == "disable" ]]; then
  zenityTitle=$"Docker Stop"
  zenityText=$"Docker Stopping, Please wait..."
fi
runAsUser "zenity --progress --title=\"$zenityTitle\" --text=\"$zenityText\" --pulsate --auto-close --no-cancel < '$pipePath'" &

# 3. Executes the root tasks.
updateDockerTask() {
  if [[ "$function" == "install" ]]; then
    pacman -Syu --noconfirm biglinux-docker-config
  elif [[ "$function" == "enable" ]]; then
    systemctl enable --now docker.service
    systemctl start docker.socket
    chmod 666 /var/run/docker.sock
  elif [[ "$function" == "disable" ]]; then
    systemctl disable --now docker.service
    systemctl stop docker.socket
  fi
  exitCode=$?
}
updateDockerTask > "$pipePath"

# 4. Cleans up the pipe
rm "$pipePath"

# 5. Shows the final result to the user, also with the correct theme.
if [[ "$exitCode" == "0" ]] && [[ "$function" == "install" ]]; then
  zenityText=$"Docker installed successfully!"
  runAsUser "zenity --info --text=\"$zenityText\""
elif [[ "$exitCode" != "0" ]] && [[ "$function" == "install" ]]; then
  zenityText=$"An error occurred while installing docker."
  runAsUser "zenity --error --text=\"$zenityText\""
fi

# 6. Exits the script with the correct exit code
exit $exitCode
