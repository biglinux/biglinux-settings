
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw
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
        
        return super().on_switch_changed(switch, state)

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
