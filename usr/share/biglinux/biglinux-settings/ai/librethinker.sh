#!/bin/bash
#Translation
export TEXTDOMAINDIR="/usr/share/locale"
export TEXTDOMAIN=biglinux-settings

check_state() {
  ! command -v unopkg &>/dev/null && echo "false" && return
  LC_ALL=C unopkg list --shared >/tmp/u_s 2>&1
  LC_ALL=C unopkg list >/tmp/u_u 2>&1
  if grep -qi "LibreThinker" /tmp/u_s /tmp/u_u || find "$HOME/.config/libreoffice" -name "*LibreThinker*" 2>/dev/null | grep -q .; then echo "true"; else echo "false"; fi
  rm -f /tmp/u_s /tmp/u_u
}

do_remove() {
  # Try to remove
  if unopkg remove -v "$1" >/tmp/u_log 2>&1; then
      # Success? Clean up residuals anyway to be sure
      find "$HOME/.config/libreoffice" -name "*LibreThinker*" -exec rm -rf {} + 2>/dev/null
      zenity --info --text=$"O LibreThinker foi removido com sucesso."
      return 0
  fi
  
  ERR=$(cat /tmp/u_log)
  
  # Lock file check
  if echo "$ERR" | grep -q ".lock"; then
    LOCK=$(echo "$ERR" | grep ".lock" | tail -1 | awk '{print $NF}' | tr -d ':')
    [ -z "$LOCK" ] || [ ! -f "$LOCK" ] && LOCK="$HOME/.config/libreoffice/4/.lock"
    
    if zenity --question --title=$"Erro de Bloqueio" --text=$"O LibreOffice parece estar bloqueado (arquivo .lock encontrado).\n\nDeseja remover o arquivo de bloqueio e tentar novamente?"; then
      rm -f "$LOCK"
      if unopkg remove -v "$1" >>/tmp/u_log 2>&1; then
          find "$HOME/.config/libreoffice" -name "*LibreThinker*" -exec rm -rf {} + 2>/dev/null
          zenity --info --text=$"O LibreThinker foi removido com sucesso."
          return 0
      fi
      ERR=$(cat /tmp/u_log)
    fi
  fi
  
  # Not deployed check
  if echo "$ERR" | grep -Eq "Não foi implantada|not deployed|IllegalArgumentException"; then
    zenity --info --text=$"A extensão não foi encontrada no registro do LibreOffice.\nArquivos residuais serão limpos."
    find "$HOME/.config/libreoffice" -name "*LibreThinker*" -exec rm -rf {} + 2>/dev/null
    return 0
  fi
  
  zenity --error --text=$"Falha ao remover o LibreThinker (ID: $1).\n\n$ERR"
  exit 1
}

toggle_state() {
  ! command -v libreoffice &>/dev/null && zenity --error --text=$"O LibreOffice não foi encontrado." && exit 1
  if [[ "$1" == "true" ]]; then
    DEST="/tmp/LibreThinker.oxt"
    (curl -L "https://extensions.libreoffice.org/assets/downloads/7313/1768943183/LibreThinker.oxt" -o "$DEST" 2>&1 | stdbuf -oL tr '\r' '\n' | grep -oE '[0-9]+' | while read -r s; do echo "$s"; echo "# "$"Baixando extensão"" ($s%)"; done) | zenity --progress --title="Download" --text=$"Iniciando..." --percentage=0 --auto-close
    echo "no" | unopkg add -v -f "$DEST" >/tmp/rl 2>&1
    sed -i 's/\\X000d\\X000a/\n/g; s/\\X000a/\n/g; s/\\Xfeff//g; s/\\\"/\"/g' /tmp/rl
    sed -n '/Mozilla/,/\[Digite/p' /tmp/rl | head -n -1 >/tmp/fl
    [ ! -s /tmp/fl ] && echo -e $"Acordo de Licença de Software da extensão LibreThinker:\nMozilla Public License Version 2.0\n\n(O texto completo será processado durante a instalação)" >/tmp/fl
    echo -e "\n\n"$"Leia o contrato acima. Para aceitar, clique em 'Sim'.\n[O sistema enviará 'sim' automaticamente ao clicar]" >>/tmp/fl
    zenity --text-info --title=$"Acordo de Licença" --filename=/tmp/fl --ok-label=$"Sim" --cancel-label=$"Não" --width=750 --height=600 || { rm -f "$DEST" /tmp/rl /tmp/fl; return 0; }
    (echo "# "$"Finalizando instalação... Fechando LibreOffice."; pkill -9 soffice.bin 2>/dev/null; sleep 1; yes "sim" | unopkg add -v -f "$DEST" >/tmp/ul 2>&1 && echo "100" || exit 1) | zenity --progress --title=$"Instalação" --text=$"Registrando..." --pulsate --auto-close
    [ $? -eq 0 ] && { (zenity --question --title=$"Sucesso" --text=$"Instalado! Abrir LibreOffice agora?" --ok-label=$"Sim" --cancel-label=$"Não" && setsid libreoffice --writer >/dev/null 2>&1 &) >/dev/null 2>&1 & } || zenity --error --text=$"Erro na instalação:\n\n$(tail -n 5 /tmp/ul)"
    rm -f "$DEST" /tmp/rl /tmp/fl /tmp/ul
  else
    pkill -9 soffice.bin 2>/dev/null
    find_id() { [ -f "$1" ] && L=$(grep -n "LibreThinker" "$1" | head -1 | cut -d: -f1) && [ -n "$L" ] && head -n "$L" "$1" | grep "Identifier:" | tail -1 | awk '{print $2}'; }
    LC_ALL=C unopkg list --shared >/tmp/u_s 2>&1; LC_ALL=C unopkg list >/tmp/u_u 2>&1
    ID=$(find_id /tmp/u_s); [ -z "$ID" ] && ID=$(find_id /tmp/u_u); [ -z "$ID" ] && ID="LibreThinker"
    do_remove "$ID"; rm -f /tmp/u_s /tmp/u_u /tmp/u_log
  fi
}
case "$1" in "check") check_state ;; "toggle") toggle_state "$2" ;; *) echo "Use: $0 {check|toggle} [true|false]" && exit 1 ;; esac
