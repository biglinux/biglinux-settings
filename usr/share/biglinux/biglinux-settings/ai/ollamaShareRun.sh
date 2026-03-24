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

# # Creates a named pipe (FIFO) for communication with Zenity
# pipePath="/tmp/ollama_share_pipe_$$"
# mkfifo "$pipePath"

# Executes the root tasks.
updateTask() {
  if [[ "$function" == "install" ]]; then
    mkdir /etc/systemd/system/ollama.service.d
    echo -e '[Service]\nEnvironment="OLLAMA_HOST=0.0.0.0"' > /etc/systemd/system/ollama.service.d/ollama.conf
    systemctl daemon-reload
    systemctl restart ollama.service
  else
    rm -f "/etc/systemd/system/ollama.service.d/ollama.conf"
    systemctl daemon-reload
    systemctl restart ollama.service
  fi
  exitCode=$?
}
updateTask #> "$pipePath"

# Cleans up the pipe
# rm "$pipePath"

localIp=$(ip route get 1 | awk '{print $7; exit}')

# Shows the final result to the user, also with the correct theme.
if [[ "$exitCode" == "0" ]] && [[ "$function" == "install" ]]; then
  zenityText=$"Ollama shared successfully.\nAddress: http://$localIp:11434"
  runAsUser "zenity --info --text=\"$zenityText\""
else
  zenityText=$"Failed to shared Ollama!"
  zenity --info --text="$zenityText"
fi

# Exits the script with the correct exit code
exit $exitCode
