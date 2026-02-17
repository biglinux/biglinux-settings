import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
import gettext
import locale
import os
import subprocess
import socket

from gi.repository import Adw, Gio, Gtk
from typing import Optional

# Set up gettext for application localization.
DOMAIN = "biglinux-settings"
LOCALE_DIR = "/usr/share/locale"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICONS_DIR = os.path.join(BASE_DIR, "icons")

locale.setlocale(locale.LC_ALL, "")
locale.bindtextdomain(DOMAIN, LOCALE_DIR)
locale.textdomain(DOMAIN)

gettext.bindtextdomain(DOMAIN, LOCALE_DIR)
gettext.textdomain(DOMAIN)
_ = gettext.gettext

class BaseSettingsPage(Adw.Bin):
    def __init__(self, main_window, **kwargs):
        super().__init__(**kwargs)
        self.main_window = main_window  # Reference to the main window to show toasts

        # Dictionaries to map UI widgets to their corresponding shell scripts
        self.switch_scripts = {}
        self.status_indicators = {}
        # Mapping: parent_switch -> list of child row widgets
        self.sub_switches = {}
        # Mapping from script path to timeout value (seconds). If None, default 90.
        self.switch_timeouts: dict[str, Optional[int]] = {}



    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("10.255.255.255", 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    def create_scrolled_content(self):
        """Cria a estrutura básica de scroll e box vertical."""
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.content_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=20, margin_top=20, margin_bottom=20, margin_start=20, margin_end=20
        )
        scrolled.set_child(self.content_box)
        self.set_child(scrolled)
        return self.content_box

    def set_search_mode(self, enabled):
        """Placeholder method for search mode compatibility."""
        pass

    # def on_reload_clicked(self, widget):
    #     """Callback for the reload button. Triggers a full UI state sync."""
    #     print("Reloading all statuses...")
    #     self.sync_all_switches()

    def create_group(self, title, description, script_group):
        """Cria um PreferencesGroup com o botão de reload automático."""
        group = Adw.PreferencesGroup()
        group.set_title(title)
        group.set_description(description)
        group.script_group = script_group

        # reload_button = Gtk.Button(
        #     icon_name="view-refresh-symbolic",
        #     valign=Gtk.Align.CENTER,
        #     tooltip_text=_("Reload all statuses")
        # )
        # reload_button.connect("clicked", lambda _: self.sync_all_switches())
        # group.set_header_suffix(reload_button)
        return group

    # Function to create a switch with a details area and clickable link.
    def create_row(self, parent_group, title, subtitle_with_markup, script_name, icon_name, info_text: Optional[str] = None, timeout: Optional[int] = None):
        """Builds a custom row mimicking Adw.ActionRow to allow for a clickable link in the subtitle."""
        # Uses Adw.PreferencesRow as a base to get the correct background and border style.
        row = Adw.PreferencesRow()

        # Main horizontal box to contain the title area and the switch.
        main_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12,
            margin_top=6,
            margin_bottom=6,
            margin_start=12,
            margin_end=12,
        )
        row.set_child(main_box)

        icon_path = os.path.join(ICONS_DIR, f"{icon_name}.svg")
        gfile = Gio.File.new_for_path(icon_path)
        icon = Gio.FileIcon.new(gfile)

        img = Gtk.Image.new_from_gicon(icon)
        img.set_pixel_size(24)
        img.add_css_class("symbolic-icon")
        main_box.append(img)

        # Vertical box for title and clickable subtitle.
        title_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, valign=Gtk.Align.CENTER)
        main_box.append(title_area)

        title_label = Gtk.Label(xalign=0, label=title)
        title_label.add_css_class("title-4")
        title_area.append(title_label)

        if subtitle_with_markup:
            subtitle_label = Gtk.Label(
                xalign=0, wrap=True, use_markup=True, label=subtitle_with_markup
            )
            subtitle_label.add_css_class("caption")
            subtitle_label.add_css_class("dim-label")
            title_area.append(subtitle_label)

        # The switch, aligned vertically center.
        switch = Gtk.Switch(valign=Gtk.Align.CENTER)

        if info_text:
            info_icon = Gtk.Image.new_from_icon_name("info")
            info_icon.set_pixel_size(28)
            info_icon.add_css_class("suggested-action")
            info_icon.add_css_class("symbolic-icon")
            info_icon.add_css_class("info-icon-blue")
            info_icon.set_valign(Gtk.Align.CENTER)
            info_icon.set_tooltip_text(info_text)
            info_icon.set_visible(False)

            setattr(switch, "_info_icon", info_icon)
            main_box.append(info_icon)

        main_box.append(switch)

        # Associate the script with the switch
        script_group = getattr(parent_group, "script_group", "default")
        script_path = os.path.join(script_group, f"{script_name}.sh")
        self.switch_scripts[switch] = script_path
        self.switch_timeouts[script_path] = timeout
        switch.connect("state-set", self.on_switch_changed)

        parent_group.add(row)
        return switch

    def create_sub_row(self, parent_group, title, subtitle_with_markup, script_name, icon_name, parent_switch: Gtk.Switch, info_text: Optional[str] = None):
        # Cria o row (mesma lógica de create_row, mas sem retorno do switch direto)
        row = Adw.PreferencesRow()
        row._is_sub_row = True

        main_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12,
            margin_top=6,
            margin_bottom=6,
            margin_start=50,
            margin_end=12,
        )
        row.set_child(main_box)

        icon_path = os.path.join(ICONS_DIR, f"{icon_name}.svg")
        gfile = Gio.File.new_for_path(icon_path)
        icon = Gio.FileIcon.new(gfile)

        img = Gtk.Image.new_from_gicon(icon)
        img.set_pixel_size(24)
        img.add_css_class("symbolic-icon")
        main_box.append(img)

        title_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, valign=Gtk.Align.CENTER)
        main_box.append(title_area)

        title_label = Gtk.Label(xalign=0, label=title)
        title_label.add_css_class("title-4")
        title_area.append(title_label)

        if subtitle_with_markup:
            subtitle_label = Gtk.Label(
                xalign=0, wrap=True, use_markup=True, label=subtitle_with_markup
            )
            subtitle_label.add_css_class("caption")
            subtitle_label.add_css_class("dim-label")
            title_area.append(subtitle_label)

        switch = Gtk.Switch(valign=Gtk.Align.CENTER)

        if info_text:
            info_icon = Gtk.Image.new_from_icon_name("info")
            info_icon.set_pixel_size(28)
            info_icon.add_css_class("suggested-action")
            info_icon.add_css_class("symbolic-icon")
            info_icon.add_css_class("info-icon-blue")
            info_icon.set_valign(Gtk.Align.CENTER)
            info_icon.set_tooltip_text(info_text)

            # Começa invisível, será controlado pelo _toggle_info_icon_visibility
            info_icon.set_visible(False)

            setattr(switch, "_info_icon", info_icon)
            main_box.append(info_icon)

        main_box.append(switch)

        script_group = getattr(parent_group, "script_group", "default")
        script_path = os.path.join(script_group, f"{script_name}.sh")
        self.switch_scripts[switch] = script_path
        switch.connect("state-set", self.on_switch_changed)

        parent_group.add(row)

        # It starts hidden
        row.set_visible(False)

        # Register the sub-switch
        self.sub_switches.setdefault(parent_switch, []).append(row)

        return switch

    def check_script_state(self, script_path):
        """Executes a script with the 'check' argument to get its current state.
        Returns True if the script's stdout is 'true', False otherwise."""
        if not os.path.exists(script_path):
            msg = _("Unavailable: script not found.")
            print(_("Script not found: {}").format(script_path))
            return (None, msg)

        try:
            result = subprocess.run(
                [script_path, "check"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                output = result.stdout.strip().lower()
                if output == "true":
                    return (True, _("Enabled"))
                elif output == "false":
                    return (False, _("Disabled"))
                elif output == "true_disabled":
                    # Returns a special string state and an explanatory message.
                    return (
                        "true_disabled",
                        _(
                            "Enabled by system configuration (e.g., Real-Time Kernel) and cannot be changed here."
                        ),
                    )
                else:
                    msg = _("Unavailable: script returned invalid output.")
                    print(
                        _("output from script {}: {}").format(
                            script_path, result.stdout.strip()
                        )
                    )
                    return (None, msg)
            else:
                msg = _("Unavailable: script returned an error.")
                print(_("Error checking state: {}").format(result.stderr))
                return (None, msg)
        except (subprocess.TimeoutExpired, Exception) as e:
            msg = _("Unavailable: failed to run script.")
            print(_("Error running script {}: {}").format(script_path, e))
            return (None, msg)

    def toggle_script_state(self, script_path, new_state, timeout: Optional[int] = None):
        """Executes a script with the 'toggle' argument to change the system state.
        Returns True on success, False on failure."""
        if not os.path.exists(script_path):
            # Use provided timeout or default to the script's configured timeout
            timeout = timeout if timeout is not None else 90
            error_msg = _("Script not found: {}").format(script_path)
            print(f"ERROR: {error_msg}")
            return False

        try:
            state_str = "true" if new_state else "false"
            result = subprocess.run(
                [script_path, "toggle", state_str],
                capture_output=True,
                text=True,
                timeout=timeout if timeout is not None else 90,
            )

            if result.returncode == 0:
                # Use the timeout that was passed to this function
                pass
                print(_("State changed successfully"))
                if result.stdout.strip():
                    print(_("Script output: {}").format(result.stdout.strip()))
                return True
            else:
                # Exit code != 0 indicates failure
                error_msg = _("Script failed with exit code: {}").format(
                    result.returncode
                )
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

    def _toggle_info_icon_visibility(self, switch: Gtk.Switch, state: bool) -> None:
        """Handles the visibility of the info icon based on the switch state.
        The icon is only visible when the switch is active (True)."""
        if hasattr(switch, "_info_icon"):
            # Check if the parent row is not hidden due to lack of support.
            row = switch.get_parent().get_parent()
            is_supported = not getattr(row, "_hidden_no_support", False)
            switch._info_icon.set_visible(state and is_supported)

    def sync_all_switches(self):
        """Synchronizes all UI widgets and disables them if their script is invalid, providing a tooltip with the reason."""
        # Sync all switches
        for switch, script_path in self.switch_scripts.items():
            row = switch.get_parent().get_parent()
            status, message = self.check_script_state(script_path)

            switch.handler_block_by_func(self.on_switch_changed)

            if status == "true_disabled":
                # State: Enabled but cannot be changed - hide it from interface.
                row.set_visible(False)
                row._hidden_no_support = True
                self._toggle_info_icon_visibility(switch, False)
            elif status is None:
                # Feature not supported - hide it from interface.
                row.set_visible(False)
                row._hidden_no_support = True
                self._toggle_info_icon_visibility(switch, False)
            else:
                row.set_sensitive(True)
                if not getattr(row, "_is_sub_row", False):
                    row.set_visible(True)
                row.set_tooltip_text(None)
                row._hidden_no_support = False
                switch.handler_block_by_func(self.on_switch_changed)
                switch.set_active(status)
                switch.handler_unblock_by_func(self.on_switch_changed)
                self._toggle_info_icon_visibility(switch, status)

            switch.handler_unblock_by_func(self.on_switch_changed)
            print(
                _("Switch {} synchronized: {}").format(
                    os.path.basename(script_path), status
                )
            )

        # Sync all status indicators
        for indicator, script_path in self.status_indicators.items():
            row = indicator.get_parent().get_parent()
            status, message = self.check_script_state(script_path)

            # Always remove all state classes first to ensure a clean slate
            indicator.remove_css_class("status-on")
            indicator.remove_css_class("status-off")
            indicator.remove_css_class("status-unavailable")

            if status is None:
                # Feature not supported - hide it from interface.
                row.set_visible(False)
                row._hidden_no_support = True
            else:
                row.set_sensitive(True)
                row.set_visible(True)
                row.set_tooltip_text(None)
                row._hidden_no_support = False
                if status:
                    indicator.add_css_class("status-on")
                else:
                    indicator.add_css_class("status-off")
            print(
                _("Indicator {} synchronized: {}").format(
                    os.path.basename(script_path), status
                )
            )

        # Handle visibility of sub‑switches
        for parent_switch, child_rows in self.sub_switches.items():
            parent_state = parent_switch.get_active()
            for child_row in child_rows:
                is_supported = not getattr(child_row, "_hidden_no_support", False)
                child_row.set_visible(parent_state and is_supported)

    def on_switch_changed(self, switch, state):
        """Callback executed when a user manually toggles a switch."""
        script_path = self.switch_scripts.get(switch)
        # Use the timeout configured for this script, if any
        timeout = self.switch_timeouts.get(script_path)

        if script_path:
            script_name = os.path.basename(script_path)
            print(_("Changing {} to {}").format(script_name, "on" if state else "off"))

            # Attempt to change the system state
            success = self.toggle_script_state(script_path, state, timeout=timeout)

            # If the script fails, revert the switch to its previous state
            # to keep the UI consistent with the actual system state.
            if not success:
                # Block signal to prevent an infinite loop
                switch.handler_block_by_func(self.on_switch_changed)
                switch.set_active(not state)
                switch.handler_unblock_by_func(self.on_switch_changed)

                print(
                    _("ERROR: Failed to change {} to {}").format(
                        script_name, "on" if state else "off"
                    )
                )
                self.main_window.show_toast(_("Failed to change setting: {}").format(script_name))
                self.sync_all_switches()
                return True
            else:
                # If this switch is a parent, adjust visibility of its sub‑switches
                if switch in self.sub_switches:
                    for child_row in self.sub_switches[switch]:
                        is_supported = not getattr(child_row, "_hidden_no_support", False)
                        child_row.set_visible(state and is_supported)

                # Refresh all switches to reflect real state
                self.sync_all_switches()

        return False

    def filter_rows(self, search_text, hide_group_headers=False):
        """Filter rows based on search text. Returns True if any rows are visible."""
        if not hasattr(self, "content_box"):
            return True

        total_visible = 0
        for child in self._get_all_children(self.content_box):
            if isinstance(child, Adw.PreferencesGroup):
                visible = self._filter_group(child, search_text, hide_group_headers)
                total_visible += visible

        return total_visible > 0

    def get_matching_rows(self, search_text):
        """Get list of rows that match search text with their parent groups."""
        if not hasattr(self, "content_box"):
            return []

        matching = []
        for child in self._get_all_children(self.content_box):
            if isinstance(child, Adw.PreferencesGroup):
                listbox = self._find_listbox_in_widget(child)
                if not listbox:
                    continue

                row = listbox.get_first_child()
                while row:
                    if isinstance(row, (Adw.PreferencesRow, Gtk.ListBoxRow)):
                        # Skip rows hidden due to lack of support
                        if getattr(row, "_hidden_no_support", False):
                            row = row.get_next_sibling()
                            continue

                        text = self._get_row_text(row).lower()
                        if search_text in text:
                            matching.append((row, child))
                    row = row.get_next_sibling()

        return matching

    def _filter_group(self, group, search_text, hide_group_headers=False):
        """Filter rows within a PreferencesGroup. Returns count of visible rows."""
        visible_count = 0

        # Save original description on first call
        if not hasattr(group, "_orig_desc"):
            group._orig_desc = group.get_description() or ""

        # Hide header during search
        if hide_group_headers and search_text:
            group.set_description("")
            suffix = group.get_header_suffix()
            if suffix:
                suffix.set_visible(False)
        else:
            # Restore original description
            group.set_description(group._orig_desc)
            suffix = group.get_header_suffix()
            if suffix:
                suffix.set_visible(True)

        # PreferencesGroup uses an internal GtkListBox
        listbox = self._find_listbox_in_widget(group)
        if not listbox:
            return 0

        row = listbox.get_first_child()
        while row:
            if isinstance(row, (Adw.PreferencesRow, Gtk.ListBoxRow)):
                # Skip rows hidden due to lack of support
                if getattr(row, "_hidden_no_support", False):
                    row = row.get_next_sibling()
                    continue

                if not search_text:
                    if getattr(row, "_is_sub_row", False):
                        parent_switch = None
                        # Procura quem é o pai desta row
                        for p_switch, children in self.sub_switches.items():
                            if row in children:
                                parent_switch = p_switch
                                break

                        if parent_switch:
                            # Visível apenas se o pai estiver ativo
                            row.set_visible(parent_switch.get_active())
                        else:
                            # Fallback seguro
                            row.set_visible(False)
                    else:
                        # Row normal fica sempre visível sem busca
                        row.set_visible(True)

                    visible_count += 1
                else:
                    text = self._get_row_text(row).lower()
                    visible = search_text in text
                    row.set_visible(visible)
                    if visible:
                        visible_count += 1
            row = row.get_next_sibling()

        # Hide group if no visible rows (but always show if no search)
        group.set_visible(visible_count > 0 or not search_text)
        return visible_count

    def _find_listbox_in_widget(self, widget):
        """Recursively find GtkListBox inside a widget."""
        if isinstance(widget, Gtk.ListBox):
            return widget
        child = widget.get_first_child() if hasattr(widget, "get_first_child") else None
        while child:
            result = self._find_listbox_in_widget(child)
            if result:
                return result
            child = child.get_next_sibling()
        return None

    def _get_row_text(self, row):
        """Extract searchable text from a row widget."""
        texts = []
        self._collect_label_texts(row, texts)
        return " ".join(texts)

    def _collect_label_texts(self, widget, texts):
        """Recursively collect text from all labels in a widget."""
        if isinstance(widget, Gtk.Label):
            text = widget.get_text() or widget.get_label() or ""
            if text:
                texts.append(text)
        child = widget.get_first_child() if hasattr(widget, "get_first_child") else None
        while child:
            self._collect_label_texts(child, texts)
            child = child.get_next_sibling()

    def _get_all_children(self, widget):
        """Get all direct children of a widget."""
        children = []
        child = widget.get_first_child() if hasattr(widget, "get_first_child") else None
        while child:
            children.append(child)
            child = child.get_next_sibling()
        return children
