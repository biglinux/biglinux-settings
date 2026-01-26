#!/bin/bash

# check current status
check_state() {
  if grep -q "plugin=ChatAI-Plasmoid" "$HOME/.config/plasma-org.kde.plasma.desktop-appletsrc"; then
    echo "true"
  else
    echo "false"
  fi
}

# change the state
toggle_state() {
  new_state="$1"
  if [[ "$new_state" == "true" ]];then
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
  exit $exitCode
}

# Executes the function based on the parameter
case "$1" in
    "check")
        check_state
        ;;
    "toggle")
        toggle_state "$2"
        ;;
    *)
        echo "Use: $0 {check|toggle} [true|false]"
        echo "  check          - Check current status"
        echo "  toggle <state> - Changes to the specified state"
        exit 1
        ;;
esac
