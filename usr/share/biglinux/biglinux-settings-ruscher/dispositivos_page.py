
from gi.repository import Gtk, Adw, GLib
from base_page import BaseSettingsPage
import gettext
import subprocess
import os

DOMAIN = 'biglinux-settings'
LOCALE_DIR = '/usr/share/locale'
gettext.bindtextdomain(DOMAIN, LOCALE_DIR)
gettext.textdomain(DOMAIN)
_ = gettext.gettext

class DispositivosPage(BaseSettingsPage):
    def __init__(self, main_window, **kwargs):
        self.jamesdsp_dialog = None
        self.jamesdsp_switch_ref = None  # Store reference to JamesDSP switch
        super().__init__(main_window, **kwargs)
        
    def populate_content(self, content_box):
        self.devices_group(content_box)

    def devices_group(self, parent):
        group = Adw.PreferencesGroup()
        group.set_title(_("Devices"))
        group.script_group = "system" # Scripts are likely in 'system' folder currently
        group.set_description(_("Manage physical devices"))
        parent.append(group)

        # Wifi
        self.Wifi_switch = self.create_row_with_clickable_link(
            group,
            _("Wifi"),
            _("Wifi On"),
            "wifi",
            icon_name="network-wireless"
        )
        # Bluetooth
        self.Bluetooth_switch = self.create_row_with_clickable_link(
            group,
            _("Bluetooth"),
            _("Bluetooth On."),
            "bluetooth",
            icon_name="bluetooth"
        )
        
        # JamesDSP - with custom handler
        self.JamesDSP_switch = self.create_jamesdsp_row(group)
        
        # Keyboard LED - with custom handler
        self.keyboard_led_switch = self.create_keyboard_led_row(group)
        
        # Inverter rolagem do mouse
        self.mouse_scroll_switch = self.create_row_with_clickable_link(
            group,
            _("Invert Mouse Scroll"),
            _("Inverts mouse scrolling without restarting the session."),
            "mouse_scroll",
            icon_name="input-mouse"
        )
    
    def create_jamesdsp_row(self, parent_group):
        """Create JamesDSP row with custom switch handling"""
        row = Adw.PreferencesRow()
        
        main_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12,
            margin_top=6,
            margin_bottom=6,
            margin_start=12,
            margin_end=12
        )
        row.set_child(main_box)
        
        # Icon
        icon_image = Gtk.Image.new_from_icon_name("audio-card-symbolic")
        icon_image.set_pixel_size(32)
        main_box.append(icon_image)
        
        # Title area
        title_area = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            hexpand=True,
            valign=Gtk.Align.CENTER
        )
        main_box.append(title_area)
        
        title_label = Gtk.Label(xalign=0, label=_("JamesDSP"))
        title_label.add_css_class("title-4")
        title_area.append(title_label)
        
        subtitle_label = Gtk.Label(
            xalign=0,
            wrap=True,
            label=_("Advanced audio effects processor that improves sound quality.")
        )
        subtitle_label.add_css_class("caption")
        subtitle_label.add_css_class("dim-label")
        title_area.append(subtitle_label)
        
        # Switch
        switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        main_box.append(switch)
        
        # Store reference for syncing
        script_path = os.path.join("system", "jamesdsp.sh")
        self.switch_scripts[switch] = script_path
        
        # Connect custom handler
        switch.connect("state-set", self.on_jamesdsp_switch_changed)
        
        # Store reference for custom sync
        self.jamesdsp_switch_ref = switch
        
        parent_group.add(row)
        return switch
    
    def create_keyboard_led_row(self, parent_group):
        """Create Keyboard LED row with custom switch handling"""
        row = Adw.PreferencesRow()
        
        main_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12,
            margin_top=6,
            margin_bottom=6,
            margin_start=12,
            margin_end=12
        )
        row.set_child(main_box)
        
        # Icon
        icon_image = Gtk.Image.new_from_icon_name("keyboard-brightness-symbolic")
        icon_image.set_pixel_size(32)
        main_box.append(icon_image)
        
        # Title area
        title_area = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            hexpand=True,
            valign=Gtk.Align.CENTER
        )
        main_box.append(title_area)
        
        title_label = Gtk.Label(xalign=0, label=_("Keyboard with LED"))
        title_label.add_css_class("title-4")
        title_area.append(title_label)
        
        subtitle_label = Gtk.Label(
            xalign=0,
            wrap=True,
            label=_("If your keyboard has LED you can enable this feature to turn it on with the system.")
        )
        subtitle_label.add_css_class("caption")
        subtitle_label.add_css_class("dim-label")
        title_area.append(subtitle_label)
        
        # Reconfigure button
        script_path = os.path.join("system", "keyboard_led.sh")
        
        reconfigure_btn = Gtk.Button()
        reconfigure_btn.set_icon_name("view-refresh-symbolic")
        reconfigure_btn.add_css_class("flat")
        reconfigure_btn.set_valign(Gtk.Align.CENTER)
        reconfigure_btn.set_tooltip_text(_("Reconfigure LED device"))
        reconfigure_btn.connect("clicked", self.on_keyboard_led_reconfigure_clicked, script_path)
        main_box.append(reconfigure_btn)
        
        # Store reference to reconfigure button for visibility control
        self.keyboard_led_reconfigure_btn = reconfigure_btn
        
        # Switch
        switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        main_box.append(switch)
        
        # Store reference for syncing
        self.switch_scripts[switch] = script_path
        
        # Connect custom handler
        switch.connect("state-set", self.on_keyboard_led_switch_changed)
        
        # Store reference for custom sync
        self.keyboard_led_switch_ref = switch
        
        parent_group.add(row)
        return switch
    
    def on_keyboard_led_reconfigure_clicked(self, button, script_path):
        """Handle reconfigure button click - reset config and show wizard"""
        # Reset configuration
        try:
            subprocess.run(
                [script_path, "reset"],
                capture_output=True,
                timeout=5
            )
        except Exception as e:
            print(f"Error resetting LED config: {e}")
        
        # Update switch state
        if hasattr(self, 'keyboard_led_switch_ref'):
            switch = self.keyboard_led_switch_ref
            switch.handler_block_by_func(self.on_keyboard_led_switch_changed)
            switch.set_active(False)
            switch.handler_unblock_by_func(self.on_keyboard_led_switch_changed)
        
        # Show configuration dialog
        self.show_keyboard_led_config_dialog(self.keyboard_led_switch_ref, script_path)
    
    def on_keyboard_led_switch_changed(self, switch, state):
        """Custom handler for Keyboard LED switch"""
        script_path = self.switch_scripts.get(switch)
        
        if state:
            # Enabling - check if configured first
            try:
                result = subprocess.run(
                    [script_path, "is_configured"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                is_configured = result.stdout.strip() == "yes"
            except:
                is_configured = False
            
            if not is_configured:
                # Not configured - show configuration dialog
                self.show_keyboard_led_config_dialog(switch, script_path)
            else:
                # Already configured - just enable
                success = self.toggle_script_state(script_path, True)
                if not success:
                    switch.handler_block_by_func(self.on_keyboard_led_switch_changed)
                    switch.set_active(False)
                    switch.handler_unblock_by_func(self.on_keyboard_led_switch_changed)
        else:
            # Disabling
            success = self.toggle_script_state(script_path, False)
            if not success:
                switch.handler_block_by_func(self.on_keyboard_led_switch_changed)
                switch.set_active(True)
                switch.handler_unblock_by_func(self.on_keyboard_led_switch_changed)
        
        return True  # Prevent default handler
    
    def show_keyboard_led_config_dialog(self, switch, script_path):
        """Show the keyboard LED configuration dialog"""
        try:
            import sys
            devices_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'devices'
            )
            if devices_path not in sys.path:
                sys.path.insert(0, devices_path)
            
            from keyboard_led_dialog import KeyboardLEDDialog
            
            def on_complete(success):
                if not success:
                    # Revert switch
                    switch.handler_block_by_func(self.on_keyboard_led_switch_changed)
                    switch.set_active(False)
                    switch.handler_unblock_by_func(self.on_keyboard_led_switch_changed)
            
            dialog = KeyboardLEDDialog(
                self.main_window,
                script_path,
                on_complete_callback=on_complete
            )
            dialog.present(self.main_window)
            
        except Exception as e:
            print(f"Error showing Keyboard LED dialog: {e}")
            switch.handler_block_by_func(self.on_keyboard_led_switch_changed)
            switch.set_active(False)
            switch.handler_unblock_by_func(self.on_keyboard_led_switch_changed)
            if hasattr(self.main_window, 'show_toast'):
                self.main_window.show_toast(_("Error opening configuration dialog"))
    
    def on_jamesdsp_switch_changed(self, switch, state):
        """Custom handler for JamesDSP switch"""
        if state:
            # Enabling - check if installed, then show preset dialog
            self.enable_jamesdsp(switch)
        else:
            # Disabling - ask if user wants to remove completely
            self.disable_jamesdsp(switch)
        
        return True  # Prevent default handler
    
    def check_jamesdsp_daemon(self):
        """Check if JamesDSP daemon is running"""
        try:
            result = subprocess.run(
                ['pgrep', '-f', 'jamesdsp'],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False
    
    def start_jamesdsp_daemon(self, callback_on_success=None):
        """Start JamesDSP daemon and call callback on success"""
        try:
            subprocess.Popen(['jamesdsp', '-t'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Wait for daemon to start
            if callback_on_success:
                GLib.timeout_add(2000, lambda: (callback_on_success(), False)[1])
        except Exception as e:
            print(f"Error starting JamesDSP daemon: {e}")
            if hasattr(self.main_window, 'show_toast'):
                self.main_window.show_toast(_("Error starting JamesDSP daemon"))
    
    def prompt_start_daemon(self, switch, on_start_callback):
        """Ask user if they want to start JamesDSP daemon"""
        dialog = Adw.AlertDialog(
            heading=_("JamesDSP Not Running"),
            body=_("JamesDSP daemon is not currently running. Would you like to start it?")
        )
        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("start", _("Start JamesDSP"))
        
        dialog.set_response_appearance("start", Adw.ResponseAppearance.SUGGESTED)
        dialog.set_default_response("start")
        dialog.set_close_response("cancel")
        
        dialog.connect("response", lambda d, r: self.on_start_daemon_response(d, r, switch, on_start_callback))
        dialog.present(self.main_window)
    
    def on_start_daemon_response(self, dialog, response, switch, callback):
        """Handle start daemon dialog response"""
        if response == "start":
            self.start_jamesdsp_daemon(callback_on_success=callback)
        else:
            # User cancelled - revert switch
            switch.handler_block_by_func(self.on_jamesdsp_switch_changed)
            switch.set_active(False)
            switch.handler_unblock_by_func(self.on_jamesdsp_switch_changed)
    
    def prompt_start_daemon_for_disable(self, switch):
        """Ask user if they want to start daemon before disabling"""
        dialog = Adw.AlertDialog(
            heading=_("JamesDSP Not Running"),
            body=_("JamesDSP daemon is not currently running. Would you like to start it first?")
        )
        dialog.add_response("no", _("No, Turn Off Switch"))
        dialog.add_response("start", _("Yes, Start JamesDSP"))
        
        dialog.set_response_appearance("start", Adw.ResponseAppearance.SUGGESTED)
        dialog.set_default_response("no")
        dialog.set_close_response("no")
        
        dialog.connect("response", lambda d, r: self.on_start_daemon_for_disable_response(d, r, switch))
        dialog.present(self.main_window)
    
    def on_start_daemon_for_disable_response(self, dialog, response, switch):
        """Handle daemon start response when trying to disable"""
        if response == "start":
            # Start daemon and then continue with disable
            self.start_jamesdsp_daemon(callback_on_success=lambda: self.continue_disable_jamesdsp(switch))
        else:
            # User said no - just turn off the switch
            switch.handler_block_by_func(self.on_jamesdsp_switch_changed)
            switch.set_active(False)
            switch.handler_unblock_by_func(self.on_jamesdsp_switch_changed)
    
    def continue_disable_jamesdsp(self, switch):
        """Continue with disable after daemon is started"""
        script_path = self.switch_scripts.get(switch)
        if not script_path:
            return
        
        # Now show the disable dialog
        self.show_disable_dialog(switch)
    
    def enable_jamesdsp(self, switch):
        """Enable JamesDSP and show preset dialog"""
        script_path = self.switch_scripts.get(switch)
        if not script_path:
            return
        
        # Check if JamesDSP is installed
        try:
            subprocess.run(['which', 'jamesdsp'], check=True, capture_output=True, timeout=2)
        except:
            # Not installed - script will install it
            success = self.toggle_script_state(script_path, True)
            if success:
                # Installed successfully - Ask if user wants to open GUI
                self.ask_open_gui_after_install(switch, script_path)
            else:
                switch.handler_block_by_func(self.on_jamesdsp_switch_changed)
                switch.set_active(False)
                switch.handler_unblock_by_func(self.on_jamesdsp_switch_changed)
            return
        
        # Check if daemon is running
        if not self.check_jamesdsp_daemon():
            # Daemon not running - ask to start
            self.prompt_start_daemon(switch, lambda: self.continue_enable_jamesdsp(switch, script_path))
        else:
            # Daemon running - continue normally
            self.continue_enable_jamesdsp(switch, script_path)
    
    def continue_enable_jamesdsp(self, switch, script_path):
        """Continue enabling JamesDSP after daemon is confirmed running"""
        success = self.toggle_script_state(script_path, True)
        
        if success:
            self.show_jamesdsp_presets()
        else:
            switch.handler_block_by_func(self.on_jamesdsp_switch_changed)
            switch.set_active(False)
            switch.handler_unblock_by_func(self.on_jamesdsp_switch_changed)

    def ask_open_gui_after_install(self, switch, script_path):
        """Ask if user wants to open JamesDSP GUI after installation"""
        dialog = Adw.AlertDialog(
            heading=_("JamesDSP Installed"),
            body=_("JamesDSP has been successfully installed.\n\nWould you like to open the application interface now to configure it?\n(You can also configure it later via the presets list)")
        )
        dialog.add_response("no", _("No, Show Presets"))
        dialog.add_response("yes", _("Yes, Open App"))
        
        dialog.set_response_appearance("yes", Adw.ResponseAppearance.SUGGESTED)
        dialog.set_default_response("yes")
        dialog.set_close_response("no")
        
        dialog.connect("response", lambda d, r: self.on_open_gui_response(d, r, switch, script_path))
        dialog.present(self.main_window)

    def on_open_gui_response(self, dialog, response, switch, script_path):
        """Handle open GUI response"""
        if response == "yes":
            try:
                # Open JamesDSP GUI independently
                subprocess.Popen(['jamesdsp'], start_new_session=True)
            except Exception as e:
                print(f"Error opening JamesDSP GUI: {e}")
        
        # Whether yes or no, allow some time if opened, then show presets
        # Opening the GUI usually starts the daemon, so we can verify and continue
        GLib.timeout_add(1500, lambda: (self.continue_enable_jamesdsp_after_install(switch), False)[1])

    def continue_enable_jamesdsp_after_install(self, switch):
        """Finalize enable process after potentially opening GUI"""
        # Daemon should be running now if GUI was opened, or if toggle script started it
        # If not, we might need to start it, but usually toggle script handles that part if we call show_presets logic
        # But here we just want to show presets because we already called toggle_script_state(True) earlier for installation
        
        # Just show presets
        self.show_jamesdsp_presets()
    
    def disable_jamesdsp(self, switch):
        """Disable JamesDSP and ask about complete removal"""
        script_path = self.switch_scripts.get(switch)
        if not script_path:
            return
        
        # Check if daemon is running first
        if not self.check_jamesdsp_daemon():
            # Daemon not running - ask if they want to start it
            self.prompt_start_daemon_for_disable(switch)
            return
        
        # Daemon is running - show disable dialog
        self.show_disable_dialog(switch)
    
    def show_disable_dialog(self, switch):
        """Show dialog to choose disable option"""
        # Ask if user wants to remove completely
        dialog = Adw.AlertDialog(
            heading=_("Disable JamesDSP"),
            body=_("Choose how to disable JamesDSP:\n\n• Just Disable: Sets master_enable=false (keeps installed)\n• Remove Completely: Uninstalls package and deletes all configuration files")
        )
        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("disable", _("Just Disable"))
        dialog.add_response("remove", _("Remove Completely"))
        
        dialog.set_response_appearance("remove", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_default_response("disable")
        dialog.set_close_response("cancel")
        
        dialog.connect("response", lambda d, r: self.on_disable_response(d, r, switch))
        dialog.present(self.main_window)
    
    def on_disable_response(self, dialog, response, switch):
        """Handle disable dialog response"""
        script_path = self.switch_scripts.get(switch)
        
        if response == "cancel":
            # Keep switch on
            switch.handler_block_by_func(self.on_jamesdsp_switch_changed)
            switch.set_active(True)
            switch.handler_unblock_by_func(self.on_jamesdsp_switch_changed)
        elif response == "disable":
            # Just disable
            success = self.toggle_script_state(script_path, False)
            if success:
                # Successfully disabled - turn off switch
                switch.handler_block_by_func(self.on_jamesdsp_switch_changed)
                switch.set_active(False)
                switch.handler_unblock_by_func(self.on_jamesdsp_switch_changed)
            else:
                # Revert switch if failed
                switch.handler_block_by_func(self.on_jamesdsp_switch_changed)
                switch.set_active(True)
                switch.handler_unblock_by_func(self.on_jamesdsp_switch_changed)
        elif response == "remove":
            # Remove completely
            self.remove_jamesdsp_complete(switch)
    
    def remove_jamesdsp_complete(self, switch):
        """Remove JamesDSP package and optionally dotfiles with verification"""
        script_path = self.switch_scripts.get(switch)
        
        try:
            # First, try to remove the package
            print("--- Starting JamesDSP removal process ---")
            result = subprocess.run(
                [script_path, "remove_package"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            print(f"Removal Script Return Code: {result.returncode}")
            print(f"Removal Script STDOUT:\n{result.stdout}")
            print(f"Removal Script STDERR:\n{result.stderr}")
            print("--- End of removal script output ---")
            
            # Check if package was actually removed
            is_installed = True
            try:
                pkg_check = subprocess.run(
                    ['pacman', '-Q', 'jamesdsp'],
                    capture_output=True,
                    timeout=2
                )
                is_installed = (pkg_check.returncode == 0)
            except:
                pass
            
            if not is_installed:
                # SUCCESS: Package removed
                
                # Update switch state
                switch.handler_block_by_func(self.on_jamesdsp_switch_changed)
                switch.set_active(False)
                switch.handler_unblock_by_func(self.on_jamesdsp_switch_changed)
                
                # Show toast
                if hasattr(self.main_window, 'show_toast'):
                    self.main_window.show_toast(_("JamesDSP package removed"))
                
                # Ask about dotfiles
                self.ask_remove_dotfiles(switch, script_path)
            else:
                # FAILURE: Package still installed (maybe cancelled or error)
                self.show_removal_failed_dialog(switch)
                
        except Exception as e:
            print(f"Error removing JamesDSP: {e}")
            self.show_removal_failed_dialog(switch)

    def show_removal_failed_dialog(self, switch):
        """Show dialog when removal fails and offer retry"""
        dialog = Adw.AlertDialog(
            heading=_("Removal Failed"),
            body=_("JamesDSP package is still installed.\n\nThe removal process may have been cancelled or failed.\nWould you like to try again?")
        )
        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("retry", _("Try Again"))
        
        dialog.set_response_appearance("retry", Adw.ResponseAppearance.SUGGESTED)
        dialog.set_default_response("retry")
        dialog.set_close_response("cancel")
        
        dialog.connect("response", lambda d, r: self.on_removal_failed_response(d, r, switch))
        dialog.present(self.main_window)

    def on_removal_failed_response(self, dialog, response, switch):
        """Handle retry response"""
        if response == "retry":
            # Retry removal
            self.remove_jamesdsp_complete(switch)
        else:
            # User gave up - revert switch to ON (since it's still installed)
            switch.handler_block_by_func(self.on_jamesdsp_switch_changed)
            switch.set_active(True)
            switch.handler_unblock_by_func(self.on_jamesdsp_switch_changed)
    
    def ask_remove_dotfiles(self, switch, script_path):
        """Ask if user wants to remove configuration files"""
        dialog = Adw.AlertDialog(
            heading=_("Remove Configuration Files?"),
            body=_("JamesDSP package has been removed.\n\nWould you like to also delete all configuration files and presets located in:\n\n• ~/.config/jamesdsp\n• ~/.local/share/jamesdsp")
        )
        dialog.add_response("no", _("Keep Files"))
        dialog.add_response("yes", _("Delete Files"))
        
        dialog.set_response_appearance("yes", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_default_response("no")
        dialog.set_close_response("no")
        
        dialog.connect("response", lambda d, r: self.on_remove_dotfiles_response(d, r, script_path))
        dialog.present(self.main_window)
    
    def on_remove_dotfiles_response(self, dialog, response, script_path):
        """Handle dotfiles removal response"""
        if response == "yes":
            try:
                subprocess.run(
                    [script_path, "remove_dotfiles"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if hasattr(self.main_window, 'show_toast'):
                    self.main_window.show_toast(_("JamesDSP removed completely"))
            except Exception as e:
                print(f"Error removing dotfiles: {e}")
        else:
            # User chose to keep files
            if hasattr(self.main_window, 'show_toast'):
                self.main_window.show_toast(_("JamesDSP package removed (config files kept)"))
    
    def show_jamesdsp_presets(self):
        """Show JamesDSP preset selection dialog"""
        try:
            # Import here to avoid circular dependency issues
            import sys
            devices_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'devices'
            )
            if devices_path not in sys.path:
                sys.path.insert(0, devices_path)
            
            from jamesdsp_dialog import JamesDSPPresetDialog
            
            if self.jamesdsp_dialog is None or not self.jamesdsp_dialog.get_visible():
                self.jamesdsp_dialog = JamesDSPPresetDialog(
                    self.main_window,
                    on_close_callback=None
                )
                self.jamesdsp_dialog.present()
        except Exception as e:
            print(f"Error showing JamesDSP dialog: {e}")
            if hasattr(self.main_window, 'show_toast'):
                self.main_window.show_toast(_("Error opening preset dialog"))
    
    def sync_all_switches(self):
        """Override to handle custom switch handlers"""
        for switch, script_path in self.switch_scripts.items():
            row = switch.get_parent().get_parent()
            status, message = self.check_script_state(script_path)
            
            # Determine which handler to use
            if switch == self.jamesdsp_switch_ref:
                handler = self.on_jamesdsp_switch_changed
            elif hasattr(self, 'keyboard_led_switch_ref') and switch == self.keyboard_led_switch_ref:
                handler = self.on_keyboard_led_switch_changed
            else:
                handler = self.on_switch_changed
            
            switch.handler_block_by_func(handler)

            if status == "true_disabled":
                row.set_sensitive(False)
                row.set_tooltip_text(message)
                switch.set_active(True)
            elif status is None:
                row.set_sensitive(False)
                row.set_tooltip_text(message)
            else:
                row.set_sensitive(True)
                row.set_tooltip_text(None)
                switch.set_active(status)

            switch.handler_unblock_by_func(handler)
            print(_("Switch {} synchronized: {}").format(os.path.basename(script_path), status))

