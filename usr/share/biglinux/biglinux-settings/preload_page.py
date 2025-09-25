import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw
import subprocess
import os
import locale
import gettext

# Set up gettext for application localization.
DOMAIN = 'biglinux-settings'
LOCALE_DIR = '/usr/share/locale'

locale.setlocale(locale.LC_ALL, '')
locale.bindtextdomain(DOMAIN, LOCALE_DIR)
locale.textdomain(DOMAIN)

gettext.bindtextdomain(DOMAIN, LOCALE_DIR)
gettext.textdomain(DOMAIN)
_ = gettext.gettext

class PreloadPage(Adw.Bin):
    """A self-contained page for managing System Tweaks."""
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
        """Constructs the main UI layout and populates it with widgets."""
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20, margin_top=20, margin_bottom=20, margin_start=20, margin_end=20)
        scrolled.set_child(content_box)

        self.usability_group(content_box)

        self.set_child(scrolled)

    def on_reload_clicked(self, widget):
        """Callback for the reload button. Triggers a full UI state sync."""
        print("Reloading all statuses...")
        self.sync_all_switches()

# Function to create a switch with a details area and clickable link.
    def create_row_with_clickable_link(self, parent_group, title, script_name, subtitle_with_markup=None):
        """Builds a custom row mimicking Adw.ActionRow to allow for a clickable link in the subtitle."""
        # Uses Adw.PreferencesRow as a base to get the correct background and border style.
        row = Adw.PreferencesRow()

        # Main horizontal box to contain the title area and the switch.
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12, margin_top=6, margin_bottom=6, margin_start=12, margin_end=12)
        row.set_child(main_box)

        # Vertical box for title and clickable subtitle.
        # hexpand=True is crucial to push the switch to the right.
        title_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, valign=Gtk.Align.CENTER)
        main_box.append(title_area)

        title_label = Gtk.Label(xalign=0, label=title)
        title_label.add_css_class("title-4")
        title_area.append(title_label)

        # Only create and add the subtitle if it's provided
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

        # The switch, aligned vertically center.
        switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        main_box.append(switch)

        # Associate the script with the switch
        script_group = getattr(parent_group, 'script_group', 'default')
        script_path = os.path.join(script_group, f"{script_name}.sh")
        self.switch_scripts[switch] = script_path
        switch.connect("state-set", self.on_switch_changed)

        parent_group.add(row)
        return switch

    def usability_group(self, parent):
        """Builds the 'Preload' preferences group."""
        group = Adw.PreferencesGroup()
        group.set_title(_("Preload"))
        group.script_group = "preload"
        group.set_description(_("Preload applications into memory to open them faster."))
        parent.append(group)

        # Create and add the reload button to the group's header
        reload_button = Gtk.Button(
            icon_name="view-refresh-symbolic",
            valign=Gtk.Align.CENTER,
            tooltip_text=_("Reload all statuses")
        )
        reload_button.connect("clicked", self.on_reload_clicked)
        group.set_header_suffix(reload_button)

        # firefox
        self.firefox_switch = self.create_row_with_clickable_link(
            group,
            _("Firefox"),
            "firefox"
        )
        # librewolf
        self.librewolf_switch = self.create_row_with_clickable_link(
            group,
            _("Librewolf"),
            "librewolf"
        )
        # brave
        self.brave_switch = self.create_row_with_clickable_link(
            group,
            _("Brave"),
            "brave"
        )
        # chrome
        self.chrome_switch = self.create_row_with_clickable_link(
            group,
            _("Chrome"),
            "chrome"
        )
        # chromium
        self.chromium_switch = self.create_row_with_clickable_link(
            group,
            _("Chromium"),
            "chromium"
        )
        # palemoon
        self.palemoon_switch = self.create_row_with_clickable_link(
            group,
            _("Palemoon"),
            "palemoon"
        )
        # opera
        self.opera_switch = self.create_row_with_clickable_link(
            group,
            _("Opera"),
            "opera"
        )
        # libreoffice
        self.libreoffice_switch = self.create_row_with_clickable_link(
            group,
            _("Libreoffice"),
            "libreoffice"
        )


    def check_script_state(self, script_path):
        """Executes a script with the 'check' argument to get its current state.
        Returns True if the script's stdout is 'true', False otherwise."""
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
                    # Returns a special string state and an explanatory message.
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
        """Executes a script with the 'toggle' argument to change the system state.
        Returns True on success, False on failure."""
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
                # Exit code != 0 indicates failure
                error_msg = _("Script failed with exit code: {}").format(result.returncode)
                print(f"ERROR: {error_msg}")

                if result.stderr.strip():
                    print(f"ERROR: Script stderr: {result.stderr.strip()}")

                if result.stdout.strip():
                    print(f"ERROR: Script stdout: {result.stdout.strip()}")

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
        """Synchronizes all UI widgets and disables them if their script is invalid, providing a tooltip with the reason."""
        # Sync all switches
        for switch, script_path in self.switch_scripts.items():
            row = switch.get_parent().get_parent()
            status, message = self.check_script_state(script_path)

            switch.handler_block_by_func(self.on_switch_changed)

            if status is None:
                row.set_visible(False)
            else:
                row.set_sensitive(True)
                row.set_tooltip_text(None)
                switch.handler_block_by_func(self.on_switch_changed)
                switch.set_active(status)
                switch.handler_unblock_by_func(self.on_switch_changed)

            switch.handler_unblock_by_func(self.on_switch_changed)
            print(_("Switch {} synchronized: {}").format(os.path.basename(script_path), status))

        # Sync all status indicators
        for indicator, script_path in self.status_indicators.items():
            row = indicator.get_parent().get_parent()
            status, message = self.check_script_state(script_path)

            # Always remove all state classes first to ensure a clean slate
            indicator.remove_css_class("status-on")
            indicator.remove_css_class("status-off")
            indicator.remove_css_class("status-unavailable")

            if status is None:
                row.set_visible(False)
            else:
                row.set_sensitive(True)
                row.set_tooltip_text(None)
                if status:
                    indicator.add_css_class("status-on")
                else:
                    indicator.add_css_class("status-off")
            print(_("Indicator {} synchronized: {}").format(os.path.basename(script_path), status))

    def on_switch_changed(self, switch, state):
        """Callback executed when a user manually toggles a switch."""
        script_path = self.switch_scripts.get(switch)

        if script_path:
            script_name = os.path.basename(script_path)
            print(_("Changing {} to {}").format(script_name, "on" if state else "off"))

            # Attempt to change the system state
            success = self.toggle_script_state(script_path, state)

            # If the script fails, revert the switch to its previous state
            # to keep the UI consistent with the actual system state.
            if not success:
                # Block signal to prevent an infinite loop
                switch.handler_block_by_func(self.on_switch_changed)
                switch.set_active(not state)
                switch.handler_unblock_by_func(self.on_switch_changed)

                print(_("ERROR: Failed to change {} to {}").format(script_name, "on" if state else "off"))
                self.show_toast(_("Failed to change setting: {}").format(script_name))

        return False
