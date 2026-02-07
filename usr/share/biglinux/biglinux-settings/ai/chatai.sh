#!/bin/bash

# check current status
if [ "$1" == "check" ]; then
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    if grep -q "plugin=ChatAI-Plasmoid" "$HOME/.config/plasma-org.kde.plasma.desktop-appletsrc"; then
      echo "true"
    else
      echo "false"
    fi
  # elif [[ "$XDG_CURRENT_DESKTOP" == *"GNOME"* ]];then
  #   if [[ "$someTest" == "true" ]];then
  #     echo "true"
  #   else
  #     echo "false"
  #   fi
  # elif [[ "$XDG_CURRENT_DESKTOP" == *"XFCE"* ]];then
  #   if [[ "$someTest" == "true" ]];then
  #     echo "true"
  #   else
  #     echo "false"
  #   fi
  # elif [[ "$XDG_CURRENT_DESKTOP" == *"Cinnamon"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"X-Cinnamon"* ]];then
  #   if [[ "$someTest" == "true" ]];then
  #     echo "true"
  #   else
  #     echo "false"
  #   fi
  fi


# change the state
elif [ "$1" == "toggle" ]; then
  state="$2"
  if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"Plasma"* ]];then
    if [ "$state" == "true" ]; then
      # check and download chatai
      if ! kpackagetool6 -t Plasma/Applet -l 2>/dev/null | grep -q "ChatAI-Plasmoid"; then
        curl -sL https://api.github.com/repos/DenysMb/ChatAI-Plasmoid/releases/latest | grep "tarball_url" | cut -d'"' -f4 | xargs curl -L -o /tmp/ChatAI-Plasmoid-latest.tar.gz
        kpackagetool6 -t Plasma/Applet -i /tmp/ChatAI-Plasmoid-latest.tar.gz
      fi
      # Unlock desktop editing mode
      qdbus6 org.kde.plasmashell /PlasmaShell evaluateScript "lockCorona(false)"
      qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
              var allPanels = panels();
              for (var i = 0; i < allPanels.length; i++) {
                  allPanels[i].addWidget('ChatAI-Plasmoid');
              }"
      if [ -e "/tmp/ChatAI-Plasmoid-latest.tar.gz" ]; then rm -f "/tmp/ChatAI-Plasmoid-latest.tar.gz"; fi
      # Lock desktop editing mode again
      qdbus6 org.kde.plasmashell /PlasmaShell evaluateScript "lockCorona(true)"
    else
      ## remove chatai
      # Unlock desktop editing mode
      qdbus6 org.kde.plasmashell /PlasmaShell evaluateScript "lockCorona(false)"
      # remove widget from painel
      qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
          panelIds.forEach(pId => {
              let p = panelById(pId);
              p.widgetIds.forEach(wId => {
                  let w = p.widgetById(wId);
                  if (w.type === 'ChatAI-Plasmoid') {
                      w.remove();
                  }
              });
          });"
      # Lock desktop editing mode again
      qdbus6 org.kde.plasmashell /PlasmaShell evaluateScript "lockCorona(true)"
      kpackagetool6 -t Plasma/Applet -r ChatAI-Plasmoid
      exitCode=$?
    fi
  # elif [[ "$XDG_CURRENT_DESKTOP" == *"GNOME"* ]];then
  #   if [ "$state" == "true" ]; then
  #       some command
  #       exitCode=$?
  #   else
  #       some command
  #       exitCode=$?
  #   fi
  # elif [[ "$XDG_CURRENT_DESKTOP" == *"XFCE"* ]];then
  #   if [ "$state" == "true" ]; then
  #       some command
  #       exitCode=$?
  #   else
  #       some command
  #       exitCode=$?
  #   fi
  # elif [[ "$XDG_CURRENT_DESKTOP" == *"Cinnamon"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"X-Cinnamon"* ]];then
  #   if [ "$state" == "true" ]; then
  #       some command
  #       exitCode=$?
  #   else
  #       some command
  #       exitCode=$?
  #   fi
  fi
  exit $exitCode
fi
