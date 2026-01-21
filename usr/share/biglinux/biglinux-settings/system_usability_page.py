
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gdk
from base_page import BaseSettingsPage
import gettext

# Set up gettext for application localization.
DOMAIN = 'biglinux-settings'
LOCALE_DIR = '/usr/share/locale'

gettext.bindtextdomain(DOMAIN, LOCALE_DIR)
gettext.textdomain(DOMAIN)
_ = gettext.gettext

import os
import subprocess
import sys

# Add 'usability' folder to path for GameModeDialog
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, 'usability'))
from gamemode_dialog import GameModeDialog

class SystemUsabilityPage(BaseSettingsPage):
    """A self-contained page for managing System Tweaks."""
    def populate_content(self, content_box):
        self.usability_group(content_box)
        self.system_group(content_box)

    def usability_group(self, parent):
        """Builds the 'Usability' preferences group."""
        group = Adw.PreferencesGroup()
        group.set_title(_("Usability"))
        group.script_group = "usability"
        group.set_description(_("User and Visual system settings"))
        parent.append(group)

        # Create and add the reload button to the group's header
        reload_button = Gtk.Button(
            icon_name="view-refresh-symbolic",
            valign=Gtk.Align.CENTER,
            tooltip_text=_("Reload all statuses")
        )
        reload_button.connect("clicked", self.on_reload_clicked)
        group.set_header_suffix(reload_button)

        # numLock
        self.numLock_switch = self.create_row_with_clickable_link(
            group,
            _("NumLock"),
            _("Initial NumLock state. Ignored if autologin is enabled."),
            "numLock",
            icon_name="system-config-keyboard"
        )
        # windowButtonOnLeftSide
        self.windowButtonOnLeftSide_switch = self.create_row_with_clickable_link(
            group,
            _("Window Button On Left Side"),
            _("Maximize, minimize, and close buttons on the left side of the window."),
            "windowButtonOnLeftSide",
            icon_name="preferences-desktop-theme-windowdecorations"
        )
        # sshStart
        self.sshStart_switch = self.create_row_with_clickable_link(
            group,
            _("SSH until next reboot"),
            _("Enable remote access via ssh until next boot."),
            "sshStart",
            icon_name="network-server"
        )

        # KZones
        self.kzones_switch = self.create_row_with_clickable_link(
            group,
            _("KZones"),
            _("Script for the KWin window manager of the KDE Plasma desktop environment"),
            "kzones",
            icon_name="preferences-system-windows-effect-flipswitch"
        )
        # Check environment
        is_kde = os.environ.get("XDG_CURRENT_DESKTOP", "").upper().find("KDE") >= 0 or \
                 os.environ.get("XDG_CURRENT_DESKTOP", "").upper().find("PLASMA") >= 0
        
        if not is_kde:
            self.kzones_switch.set_sensitive(False)
            self.kzones_switch.set_tooltip_text(_("This feature is only available for KDE Plasma."))

        # Game Mode Booster
        # Game Mode Booster
        self.gamemode_switch = self.create_row_with_clickable_link(
            group,
            _("Game Mode Booster"),
            _("Combination of daemon and library that allows games to request a set of optimizations be temporarily applied to the operating system and/or the game process."),
            "biglinux_ultimate_booster",
            icon_name="input-gaming"
        )
        
        # Info Button
        self.gamemode_info_btn = Gtk.Button(icon_name="dialog-information-symbolic")
        self.gamemode_info_btn.add_css_class("flat")
        self.gamemode_info_btn.set_tooltip_text(_("Instructions"))
        self.gamemode_info_btn.set_valign(Gtk.Align.CENTER)
        self.gamemode_info_btn.set_visible(False)
        
        self.gamemode_switch.get_parent().append(self.gamemode_info_btn)
        
        self.gamemode_info_btn.connect("clicked", self.on_gamemode_info_clicked)
        self.gamemode_switch.connect("notify::active", self.update_gamemode_info_visibility)

    def system_group(self, parent):
        """Builds the 'System' preferences group."""
        group = Adw.PreferencesGroup()
        group.set_title(_("System"))
        group.script_group = "system"
        group.set_description(_("General system settings"))
        parent.append(group)
        # sshEnable
        self.sshEnable_switch = self.create_row_with_clickable_link(
            group,
            _("SSH always on"),
            _("Turn on ssh remote access at boot."),
            "sshEnable",
            icon_name="network-server"
        )
        # fastGrub
        self.fastGrub_enable_switch = self.create_row_with_clickable_link(
            group,
            _("Fast Grub"),
            _("Decreases grub display time."),
            "fastGrub",
            icon_name="biglinux-grub-restore"
        )
        # bigMount
        self.bigMount_enable_switch = self.create_row_with_clickable_link(
            group,
            _("Auto-mount Partitions"),
            _("Auto mount partitions in internal disks on boot."),
            "bigMount",
            icon_name="partitionmanager"
        )
        # Meltdown mitigations
        link_meltdown = "https://meltdownattack.com"
        self.meltdownMitigations_switch = self.create_row_with_clickable_link(
            group,
            _("Meltdown Mitigations off"),
            _("Using mitigations=off will make your machine faster and less secure! For more information see: <a href='{link}'>{link}</a>").format(link=link_meltdown),
            "meltdownMitigations",
            icon_name="security-high"
        )
        # noWatchdog
        self.noWatchdog_switch = self.create_row_with_clickable_link(
            group,
            _("noWatchdog"),
            _("Disables the hardware watchdog and TSC clocksource systems, maintaining high performance but removing automatic protections against system crashes."),
            "noWatchdog",
            icon_name="mail-thread-watch"
        )



    def on_switch_changed(self, switch, state):
        if hasattr(self, 'kzones_switch') and switch == self.kzones_switch:
             # Custom logic for KZones
            script_path = self.switch_scripts.get(switch)
            if script_path:
                print(_("Changing {} to {}").format("KZones", "on" if state else "off"))
                success = self.toggle_script_state(script_path, state)
                
                if not success:
                    # Revert
                    switch.handler_block_by_func(self.on_switch_changed)
                    switch.set_active(not state)
                    switch.handler_unblock_by_func(self.on_switch_changed)
                    if hasattr(self.main_window, 'show_toast'):
                            self.main_window.show_toast(_("Failed to change setting: {}").format("KZones"))
                else:
                    # Success - Ask for restart
                    self.show_restart_kwin_dialog()
                
                return True # We handled it

        if hasattr(self, 'gamemode_switch') and switch == self.gamemode_switch:
            script_path = self.switch_scripts.get(switch)
            if state:
                # Enable: Show Disclaimer first
                def on_confirm():
                    progress_dlg = GameModeDialog(
                        self.main_window, 
                        script_path, 
                        action="start",
                        on_close_callback=lambda success: self.on_gamemode_dialog_closed(switch, success, True)
                    )
                    progress_dlg.present()
                
                def on_cancel():
                    switch.handler_block_by_func(self.on_switch_changed)
                    switch.set_active(False)
                    switch.handler_unblock_by_func(self.on_switch_changed)

                self.show_gamemode_disclaimer(script_path, on_confirm, on_cancel)
                return True
            else:
                # Disable: Just launch Progress Dialog
                progress_dlg = GameModeDialog(
                    self.main_window, 
                    script_path, 
                    action="stop",
                    on_close_callback=lambda success: self.on_gamemode_dialog_closed(switch, success, False)
                )
                progress_dlg.present()
                return True

        return super().on_switch_changed(switch, state)

    def on_gamemode_dialog_closed(self, switch, success, target_state):
        if not success:
            # Revert switch if failed
            switch.handler_block_by_func(self.on_switch_changed)
            switch.set_active(not target_state)
            switch.handler_unblock_by_func(self.on_switch_changed)
        else:
            # Success, switch is already in correct state visually
            pass
        
            pass

    def show_restart_kwin_dialog(self):
        dialog = Adw.MessageDialog(
            transient_for=self.main_window,
            heading=_("Restart KWin?"),
            body=_("To apply the changes, the KWin window manager needs to be restarted. Do you want to restart it now?"),
        )
        dialog.add_response("cancel", _("No"))
        dialog.add_response("restart", _("Yes"))
        dialog.set_default_response("restart")
        dialog.set_close_response("cancel")
        dialog.connect("response", self.on_restart_kwin_response)
        dialog.present()

    def on_restart_kwin_response(self, dialog, response):
        if response == "restart":
             script_path = self.switch_scripts.get(self.kzones_switch)
             if script_path:
                 subprocess.run([script_path, "reload"])

    def update_gamemode_info_visibility(self, switch, param):
        self.gamemode_info_btn.set_visible(switch.get_active())

    def on_gamemode_info_clicked(self, button):
        script_path = self.switch_scripts.get(self.gamemode_switch)
        
        def on_confirm():
             # Re-start/Verify if user clicks enable again
             progress_dlg = GameModeDialog(
                self.main_window, 
                script_path, 
                action="start",
                on_close_callback=lambda success: self.on_gamemode_dialog_closed(self.gamemode_switch, success, True)
            )
             progress_dlg.present()

        self.show_gamemode_disclaimer(script_path, on_confirm)

    def show_gamemode_disclaimer(self, script_path, on_confirm, on_cancel=None):
        dialog = Adw.MessageDialog(
            transient_for=self.main_window,
            heading=_("Game Mode Booster Instructions"),
            body=_("To ensure Game Mode works correctly, you may need to apply specific launch options for your games.")
        )

        # Content Box
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        # Instructions Group
        group = Adw.PreferencesGroup()
        group.set_title(_("Launch Options"))
        group.set_description(_("Copy and paste these commands into your game's launch options."))
        content_box.append(group)

        # Helper to add command rows
        def add_command_row(title, command, icon):
            row = Adw.ActionRow()
            row.set_title(title)
            row.set_subtitle(command)
            row.add_prefix(Gtk.Image.new_from_icon_name(icon))
            
            # Copy Button
            btn_copy = Gtk.Button(icon_name="edit-copy-symbolic")
            btn_copy.add_css_class("flat")
            btn_copy.set_tooltip_text(_("Copy to clipboard"))
            btn_copy.connect("clicked", lambda b: Gdk.Display.get_default().get_clipboard().set(command))
            
            row.add_suffix(btn_copy)
            group.add(row)

        add_command_row(_("Run manually"), "gamemoderun ./game", "utilities-terminal-symbolic")
        add_command_row(_("Steam Launch Options"), "gamemoderun %command%", "steam")
        add_command_row(_("Older Versions (< 1.3)"), 'LD_PRELOAD="$LD_PRELOAD:/usr/$LIB/libgamemodeauto.so.0"', "application-legacy-symbolic")

        # Note Label
        note_label = Gtk.Label(label=_("Note: The backslash in $LIB is required for the older versions command."))
        note_label.add_css_class("dim-label")
        note_label.set_wrap(True)
        note_label.set_halign(Gtk.Align.START)
        content_box.append(note_label)

        dialog.set_extra_child(content_box)

        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("enable", _("Enable"))
        dialog.set_default_response("enable")
        dialog.set_close_response("cancel")
        
        def on_response(dlg, response):
            if response == "enable":
                on_confirm()
            else:
                if on_cancel:
                    on_cancel()

        dialog.connect("response", on_response)
        # Expand width for better readabilty
        dialog.set_body_use_markup(True) 
        
        # We need to present it
        dialog.present()
