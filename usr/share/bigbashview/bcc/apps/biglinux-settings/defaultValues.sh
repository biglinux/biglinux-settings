#!/bin/bash
##################################
#  Author1: Bruno Goncalves (www.biglinux.com.br) 
#  Author2: Barnabé di Kartola
#  Author3: Rafael Ruscher (rruscher@gmail.com)  
#  Date:    2022/02/28 
#  Modified:2022/07/10 
#  
#  Description: Themes, Desktop and Ajust usage of BigLinux 
#  
# Licensed by GPL V2 or greater
##################################

# Translation
export TEXTDOMAINDIR="/usr/share/locale"
export TEXTDOMAIN=biglinux-settings

# Import functions
. /usr/share/bigbashview/bcc/shell/bbvFunctions

# if not change use as default values
id="${PWD/*\//}"
folder_complete="${PWD%/*}"
sectionFolder="${folder_complete##*/}"

# Add default config to switch
defaultConfigSwitch='icon="$sectionFolder/$id/icon.svg" text="$name" check="$checked" run="$sectionFolder/$id/script.run" border="1" id="$id" paddingVertical="3"'

# Add default config to line_button_modal
defaultConfigLineButtonModal='icon="$id/icon.svg" text="$name" buttonText="$OPEN" id="$id" paddingVertical="3" border="1" buttonModal="modal"' 
