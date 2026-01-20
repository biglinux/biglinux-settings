
from gi.repository import Gtk, Adw
from base_page import BaseSettingsPage
import gettext

DOMAIN = 'biglinux-settings'
LOCALE_DIR = '/usr/share/locale'
gettext.bindtextdomain(DOMAIN, LOCALE_DIR)
gettext.textdomain(DOMAIN)
_ = gettext.gettext


import sys
import os
import subprocess
# Add 'ai' folder to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, 'ai'))

from krita_ai_dialog import KritaAIDialog
from chatai_dialog import ChatAIDialog

class AIPage(BaseSettingsPage):
    def populate_content(self, content_box):
        self.ai_group(content_box)

    def ai_group(self, parent):
        group = Adw.PreferencesGroup()
        group.set_title(_("Artificial Intelligence"))
        group.script_group = "ai"
        group.set_description(_("AI settings and tools"))
        parent.append(group)
        
        # Generative AI for Krita
        self.krita_ai_switch = self.create_row_with_clickable_link(
            group,
            _("Generative AI for Krita"),
            _("This is a plugin to use generative AI in painting and image editing workflows directly in Krita."),
            "krita_ai",
            icon_name="krita"
        )

        # ChatAI
        self.chatai_switch = self.create_row_with_clickable_link(
            group,
            _("ChatAI"),
            _("A variety of chats like Plasmoid for your KDE Plasma desktop."),
            "chatai",
            icon_name="utilities-terminal" # Placeholder icon, user didn't specify
        )

    def on_switch_changed(self, switch, state):
        if switch == self.chatai_switch:
            script_path = self.switch_scripts.get(switch)
            if state:
                # Show Disclaimer Dialog
                dialog = Adw.MessageDialog(
                    transient_for=self.main_window,
                    heading=_("ChatAI Requirements"),
                    body=_("This resource requires at least 16 GB of RAM and is not recommended for legacy computers.")
                )
                dialog.add_response("cancel", _("Cancel"))
                dialog.add_response("accept", _("Accept"))
                
                dialog.set_default_response("accept")
                dialog.set_close_response("cancel")
                
                def on_disclaimer_response(dlg, response):
                    if response == "accept":
                        # Proceed to install
                        install_dialog = ChatAIDialog(self.main_window, script_path, on_close_callback=lambda success: self.on_chatai_dialog_closed(switch, success))
                        install_dialog.present()
                    else:
                        # Cancelled - Toggle switch back to OFF
                        switch.handler_block_by_func(self.on_switch_changed)
                        switch.set_active(False)
                        switch.handler_unblock_by_func(self.on_switch_changed)

                dialog.connect("response", on_disclaimer_response)
                dialog.present()
                return False
                
            else:
                # Remove process
                subprocess.run([script_path, "remove"])
                
                # Ask to restart Plasma Shell
                dialog = Adw.MessageDialog(
                    transient_for=self.main_window,
                    heading=_("Restart Plasma Shell"),
                    body=_("To apply changes, it is recommended to restart Plasma Shell. Do you want to restart it now?")
                )
                dialog.add_response("cancel", _("No"))
                dialog.add_response("restart", _("Yes"))
                
                dialog.set_default_response("restart")
                dialog.set_close_response("cancel")
                
                def on_restart_response(dlg, response):
                    if response == "restart":
                        # Execute restart command
                        subprocess.run("killall plasmashell && plasmashell &", shell=True)
                
                dialog.connect("response", on_restart_response)
                dialog.present()
                
                return False

        if switch == self.krita_ai_switch:
            if state:
                # Install process
                # Check directly if script exists
                script_path = self.switch_scripts.get(switch)
                
                # Show Dialog
                dialog = KritaAIDialog(self.main_window, script_path, on_close_callback=lambda success: self.on_krita_dialog_closed(switch, success))
                dialog.present()
                
                # Block handler to prevent loop if dialog fails (we toggle back manually if needed)
                return True
            else:
                # Remove process - Ask for confirmation type
                dialog = Adw.MessageDialog(
                    transient_for=self.main_window,
                    heading=_("Disable Krita AI"),
                    body=_("How do you want to disable/remove the plugin?")
                )
                dialog.add_response("cancel", _("Cancel"))
                dialog.add_response("disable", _("Disable Only"))
                dialog.add_response("remove_all", _("Remove Krita & Data"))
                
                # Highlight the least destructive option
                dialog.set_default_response("disable")
                dialog.set_close_response("cancel")
                
                # Context for callback
                script_path = self.switch_scripts.get(switch)
                
                def on_remove_response(dlg, response):
                    if response == "disable":
                        subprocess.run([script_path, "remove_plugin_only"])
                    elif response == "remove_all":
                        subprocess.run([script_path, "remove_complete"])
                    else:
                        # Cancelled - Toggle switch back to ON
                        switch.handler_block_by_func(self.on_switch_changed)
                        switch.set_active(True)
                        switch.handler_unblock_by_func(self.on_switch_changed)

                dialog.connect("response", on_remove_response)
                dialog.present()
                
                # Return False so visual state changes to off immediately, but we might revert if cancelled.
                # Actually if we return False, switch toggles. If user cancels, we toggle back in callback.
                return False
        
        return super().on_switch_changed(switch, state)

    def on_krita_dialog_closed(self, switch, success):
        if not success:
            switch.handler_block_by_func(self.on_switch_changed)
            switch.set_active(False)
            switch.handler_unblock_by_func(self.on_switch_changed)
        else:
             # Sync state?
            pass

    def on_chatai_dialog_closed(self, switch, success):
        if not success:
            switch.handler_block_by_func(self.on_switch_changed)
            switch.set_active(False)
            switch.handler_unblock_by_func(self.on_switch_changed)
