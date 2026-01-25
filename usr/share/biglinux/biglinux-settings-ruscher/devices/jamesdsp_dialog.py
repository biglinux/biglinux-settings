
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gio
import subprocess
import gettext

DOMAIN = 'biglinux-settings'
_ = gettext.gettext

class JamesDSPPresetDialog(Adw.Window):
    """Dialog for selecting and loading JamesDSP presets"""
    
    def __init__(self, parent_window, on_close_callback=None):
        super().__init__(modal=True, transient_for=parent_window)
        self.set_default_size(500, 600)
        self.set_title(_("JamesDSP Preset Selector"))
        
        self.on_close_callback = on_close_callback
        
        # Main content box
        self.main_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
            margin_top=12,
            margin_bottom=12,
            margin_start=12,
            margin_end=12
        )
        self.set_content(self.main_box)
        
        # Header with title
        title_label = Gtk.Label(label=_("JamesDSP Presets"))
        title_label.add_css_class("title-2")
        title_label.set_margin_bottom(12)
        self.main_box.append(title_label)
        
        # Status label
        self.status_label = Gtk.Label()
        self.status_label.set_margin_bottom(6)
        self.main_box.append(self.status_label)
        
        # Scrolled window for presets list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        scrolled.set_margin_bottom(12)
        scrolled.set_min_content_height(300)
        self.main_box.append(scrolled)
        
        # ListBox for presets
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.listbox.add_css_class("boxed-list")
        self.listbox.connect('row-activated', self.on_preset_activated)
        scrolled.set_child(self.listbox)
        
        # Button box
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, halign=Gtk.Align.CENTER)
        self.main_box.append(button_box)
        
        # Refresh button
        refresh_button = Gtk.Button(label=_("Refresh"))
        refresh_button.set_icon_name("view-refresh-symbolic")
        refresh_button.connect('clicked', self.load_presets)
        button_box.append(refresh_button)
        
        # Close button
        close_button = Gtk.Button(label=_("Close"))
        close_button.connect('clicked', self.on_close_clicked)
        close_button.add_css_class("suggested-action")
        button_box.append(close_button)
        
        # Load presets initially
        self.load_presets(None)
    
    def load_presets(self, button):
        """Load available presets"""
        # Clear current list
        while child := self.listbox.get_first_child():
            self.listbox.remove(child)
        
        # Fetch presets directly
        try:
            result = subprocess.run(
                ['jamesdsp', '--list-presets'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else _("Unknown error")
                error_row = Adw.ActionRow(
                    title=_("Error fetching presets"),
                    subtitle=error_msg
                )
                self.listbox.append(error_row)
                self.status_label.set_label(_("❌ Error loading presets"))
                return
            
            # Parse output - jamesdsp --list-presets outputs one preset per line
            lines = result.stdout.strip().split('\n')
            presets = []
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):  # Skip empty lines and comments
                    # Remove .conf extension if present
                    if line.endswith('.conf'):
                        line = line[:-5]  # Remove last 5 characters (.conf)
                    presets.append(line)
            
            if not presets:
                empty_row = Adw.ActionRow(title=_("No presets found"))
                self.listbox.append(empty_row)
                self.status_label.set_label(_("No presets available"))
                return
            
            # Add presets to list
            for preset in presets:
                row = Adw.ActionRow(title=preset)
                
                # Add icon
                icon = Gtk.Image.new_from_icon_name("audio-x-generic-symbolic")
                row.add_prefix(icon)
                
                # Add quick load button
                quick_button = Gtk.Button()
                quick_button.set_icon_name("media-playback-start-symbolic")
                quick_button.add_css_class('flat')
                quick_button.set_tooltip_text(_("Load {}").format(preset))
                quick_button.connect('clicked', lambda b, p=preset: self.load_preset(p))
                row.add_suffix(quick_button)
                
                self.listbox.append(row)
            
            self.status_label.set_label(_("✅ Found {} presets").format(len(presets)))
            
        except FileNotFoundError:
            error_row = Adw.ActionRow(title=_("JamesDSP not installed"))
            self.listbox.append(error_row)
            self.status_label.set_label(_("❌ JamesDSP not found"))
        except Exception as e:
            error_row = Adw.ActionRow(title=_("Error: {}").format(str(e)))
            self.listbox.append(error_row)
            self.status_label.set_label(_("❌ Error"))
    
    def on_preset_activated(self, listbox, row):
        """Handle preset row activation"""
        if isinstance(row, Adw.ActionRow):
            preset_name = row.get_title()
            # Only load if it's not a special row
            if preset_name and not preset_name.startswith(_("JamesDSP")):
                self.load_preset(preset_name)
    
    def load_preset(self, preset_name):
        """Load the selected preset"""
        try:
            print(f"Attempting to load preset: {preset_name}")
            result = subprocess.run(
                ['jamesdsp', '--load-preset', preset_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            print(f"Return code: {result.returncode}")
            print(f"Stdout: {result.stdout}")
            print(f"Stderr: {result.stderr}")
            
            # JamesDSP sometimes returns non-zero even on success
            # So we always show success unless there's a clear error
            if "error" in result.stderr.lower() or "failed" in result.stderr.lower():
                # Show error only if there's an actual error message
                error_details = f"Command: jamesdsp --load-preset {preset_name}\n"
                error_details += f"Return code: {result.returncode}\n\n"
                if result.stdout:
                    error_details += f"Output: {result.stdout}\n"
                if result.stderr:
                    error_details += f"Error: {result.stderr}"
                
                self.show_message(
                    _("Error"),
                    _("Failed to load preset:\n\n{}").format(error_details)
                )
            else:
                # Assume success
                self.show_message(
                    _("Success"),
                    _("Preset '{}' loaded successfully!").format(preset_name)
                )
                self.status_label.set_label(_("Preset '{}' loaded").format(preset_name))
                
        except Exception as e:
            self.show_message(
                _("Error"),
                _("Exception loading preset:\n{}").format(str(e))
            )
    
    def show_message(self, title, message):
        """Show alert dialog"""
        dialog = Adw.AlertDialog(
            heading=title,
            body=message
        )
        dialog.add_response("ok", _("OK"))
        dialog.set_default_response("ok")
        dialog.set_close_response("ok")
        dialog.present(self)
    
    def on_close_clicked(self, button):
        """Handle close button click"""
        if self.on_close_callback:
            self.on_close_callback()
        self.close()
