
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw
import subprocess
import os
import gettext

# Set up gettext for application localization.
DOMAIN = 'biglinux-settings'
LOCALE_DIR = '/usr/share/locale'

gettext.bindtextdomain(DOMAIN, LOCALE_DIR)
gettext.textdomain(DOMAIN)
_ = gettext.gettext

class BaseSettingsPage(Adw.Bin):
    """Base class for settings pages containing common logic."""
    def __init__(self, main_window, **kwargs):
        super().__init__(**kwargs)
        self.main_window = main_window # Reference to the main window to show toasts

        # Dictionaries to map UI widgets to their corresponding shell scripts
        self.switch_scripts = {}
        self.status_indicators = {}

        # Build the user interface
        self.setup_ui()

        # Sync the state of the switches on initialization
        self.sync_all_switches()

    def setup_ui(self):
        """Constructs the main UI layout. Subclasses should override or extend this."""
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20, margin_top=20, margin_bottom=20, margin_start=20, margin_end=20)
        scrolled.set_child(content_box)
        
        self.populate_content(content_box)

        self.set_child(scrolled)
    
    def populate_content(self, content_box):
        """Method to be overridden by subclasses to add content."""
        pass

    def on_reload_clicked(self, widget):
        """Callback for the reload button. Triggers a full UI state sync."""
        print("Reloading all statuses...")
        self.sync_all_switches()

    def create_row_with_clickable_link(self, parent_group, title, subtitle_with_markup, script_name, icon_name=None):
        """Builds a custom row mimicking Adw.ActionRow to allow for a clickable link in the subtitle."""
        row = Adw.PreferencesRow()

        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12, margin_top=6, margin_bottom=6, margin_start=12, margin_end=12)
        row.set_child(main_box)

        if icon_name:
            icon_image = Gtk.Image.new_from_icon_name(icon_name)
            icon_image.set_pixel_size(32)
            main_box.append(icon_image)

        title_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, valign=Gtk.Align.CENTER)
        main_box.append(title_area)

        title_label = Gtk.Label(xalign=0, label=title)
        title_label.add_css_class("title-4")
        title_area.append(title_label)
        
        if subtitle_with_markup:
            subtitle_label = Gtk.Label(
                xalign=0,
                wrap=True,
                use_markup=True,
                label=subtitle_with_markup
            )
            subtitle_label.add_css_class("caption")
            subtitle_label.add_css_class("dim-label")
            title_area.append(subtitle_label)

        switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        main_box.append(switch)

        script_group = getattr(parent_group, 'script_group', 'default')
        script_path = os.path.join(script_group, f"{script_name}.sh")
        self.switch_scripts[switch] = script_path
        switch.connect("state-set", self.on_switch_changed)

        parent_group.add(row)
        return switch

    def check_script_state(self, script_path):
        """Executes a script with the 'check' argument to get its current state."""
        if not os.path.exists(script_path):
            msg = _("Unavailable: script not found.")
            print(_("Script not found: {}").format(script_path))
            return (None, msg)

        try:
            result = subprocess.run([script_path, "check"],
            capture_output=True,
            text=True,
            timeout=10)
            if result.returncode == 0:
                output = result.stdout.strip().lower()
                if output == "true":
                    return (True, _("Enabled"))
                elif output == "false":
                    return (False, _("Disabled"))
                elif output == "true_disabled":
                    return ("true_disabled", _("Enabled by system configuration (e.g., Real-Time Kernel) and cannot be changed here."))
                else:
                    msg = _("Unavailable: script returned invalid output.")
                    print(_("Invalid output from script {}: {}").format(script_path, result.stdout.strip()))
                    return (None, msg)
            else:
                msg = _("Unavailable: script returned an error.")
                print(_("Error checking state: {}").format(result.stderr))
                return (None, msg)
        except (subprocess.TimeoutExpired, Exception) as e:
            msg = _("Unavailable: failed to run script.")
            print(_("Error running script {}: {}").format(script_path, e))
            return (None, msg)

    def toggle_script_state(self, script_path, new_state):
        if not os.path.exists(script_path):
            error_msg = _("Script not found: {}").format(script_path)
            print(f"ERROR: {error_msg}")
            return False

        try:
            state_str = "true" if new_state else "false"
            result = subprocess.run([script_path, "toggle", state_str],
            capture_output=True,
            text=True,
            timeout=30)

            if result.returncode == 0:
                print(_("State changed successfully"))
                if result.stdout.strip():
                    print(_("Script output: {}").format(result.stdout.strip()))
                return True
            else:
                error_msg = _("Script failed with exit code: {}").format(result.returncode)
                print(f"ERROR: {error_msg}")
                if result.stderr.strip():
                    print(f"ERROR: Script stderr: {result.stderr.strip()}")
                return False

        except subprocess.TimeoutExpired:
            error_msg = _("Script timeout: {}").format(script_path)
            print(f"ERROR: {error_msg}")
            return False
        except Exception as e:
            error_msg = _("Error running script {}: {}").format(script_path, e)
            print(f"ERROR: {error_msg}")
            return False

    def sync_all_switches(self):
        for switch, script_path in self.switch_scripts.items():
            row = switch.get_parent().get_parent()
            status, message = self.check_script_state(script_path)
            
            # Use visible instead of sensitive if status is None based on PreloadPage logic?
            # SystemUsabilityPage logic uses sensitive(False) for None.
            # PreloadPage uses visible(False).
            # The most robust is likely sensitive(False) with tooltip, or visible(False) if completely broken.
            # I will stick to SystemUsabilityPage logic (sensitive=False) as it's more informative usually.
            
            switch.handler_block_by_func(self.on_switch_changed)

            if status == "true_disabled":
                row.set_sensitive(False)
                row.set_tooltip_text(message)
                switch.set_active(True)
            elif status is None:
                # Let's support both behaviors or pick one. 
                # If script missing, we probably want to disable.
                row.set_sensitive(False)
                row.set_tooltip_text(message)
            else:
                row.set_sensitive(True)
                row.set_tooltip_text(None)
                switch.handler_block_by_func(self.on_switch_changed)
                switch.set_active(status)
                switch.handler_unblock_by_func(self.on_switch_changed)

            switch.handler_unblock_by_func(self.on_switch_changed)
            print(_("Switch {} synchronized: {}").format(os.path.basename(script_path), status))

        for indicator, script_path in self.status_indicators.items():
            # Similar logic for indicators if any
            pass

    def on_switch_changed(self, switch, state):
        script_path = self.switch_scripts.get(switch)
        if script_path:
            script_name = os.path.basename(script_path)
            print(_("Changing {} to {}").format(script_name, "on" if state else "off"))
            success = self.toggle_script_state(script_path, state)
            if not success:
                switch.handler_block_by_func(self.on_switch_changed)
                switch.set_active(not state)
                switch.handler_unblock_by_func(self.on_switch_changed)
                print(_("ERROR: Failed to change {} to {}").format(script_name, "on" if state else "off"))
                
                # Check if main_window has show_toast
                if hasattr(self.main_window, 'show_toast'):
                     self.main_window.show_toast(_("Failed to change setting: {}").format(script_name))
        return False
