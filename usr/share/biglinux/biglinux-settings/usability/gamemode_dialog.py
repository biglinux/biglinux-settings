
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib
import subprocess
import gettext
import threading
import os

DOMAIN = 'biglinux-settings'
_ = gettext.gettext

class GameModeDialog(Adw.Window):
    def __init__(self, parent_window, script_path, action="start", on_close_callback=None):
        super().__init__(modal=True, transient_for=parent_window)
        self.set_default_size(550, 600)
        
        self.script_path = script_path
        self.action = action # "start" or "stop"
        self.on_close_callback = on_close_callback
        self.is_running = False
        self.collected_log = []

        title = _("Game Mode Booster Activation") if action == "start" else _("Game Mode Booster Deactivation")
        self.set_title(title)

        # Main content box
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_content(self.main_box)

        # Status Page (Initially showing progress)
        self.status_page = Adw.StatusPage()
        self.status_page.set_title(_("Initializing..."))
        self.status_page.set_icon_name("input-gaming")
        self.status_page.set_vexpand(True)
        self.main_box.append(self.status_page)

        # Progress Bar within a clamp
        self.progress_bar = Gtk.ProgressBar()
        clamp = Adw.Clamp(maximum_size=400)
        clamp.set_child(self.progress_bar)
        self.status_page.set_child(clamp)

        # Start process automatically
        self.start_process()

    def update_status(self, text):
        self.status_page.set_description(GLib.markup_escape_text(text))

    def update_progress(self, fraction):
        self.progress_bar.set_fraction(fraction)

    def start_process(self):
        self.is_running = True
        threading.Thread(target=self.process_thread, daemon=True).start()

    def process_thread(self):
        GLib.idle_add(self.update_status, _("Optimizing system..."))
        
        cmd_arg = "start_gui" if self.action == "start" else "stop_gui"
        cmd = ["pkexec", self.script_path, cmd_arg]
        
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    text = line.strip()
                    if text.startswith("PROGRESS:"):
                        try:
                                val = float(text.split(":")[1]) / 100.0
                                GLib.idle_add(self.update_progress, val)
                        except:
                            pass
                    elif text.startswith("STATUS:"):
                        status_msg = text.split(":", 1)[1]
                        GLib.idle_add(self.update_status, status_msg)
                    else:
                        # Collect full text for report parsing
                        self.collected_log.append(text)
            
            rc = process.poll()
            GLib.idle_add(self.on_process_finished, rc)
            
        except Exception as e:
            GLib.idle_add(self.update_status, f"Error: {e}")
            GLib.idle_add(self.on_process_finished, 1)

    def on_process_finished(self, return_code):
        self.is_running = False
        
        if return_code == 0:
            self.show_report_view()
            if self.on_close_callback:
                self.on_close_callback(True)
        elif return_code == 126 or return_code == 127:
             self.status_page.set_title(_("Cancelled"))
             self.status_page.set_description(_("Authentication was cancelled."))
             self.status_page.set_icon_name("dialog-error-symbolic")
             self.add_close_button()
             if self.on_close_callback:
                self.on_close_callback(False)
        else:
            self.status_page.set_title(_("Failed"))
            self.status_page.set_description(_("Process failed. Check logs."))
            self.status_page.set_icon_name("dialog-error-symbolic")
            self.add_close_button()
            if self.on_close_callback:
                self.on_close_callback(False)

    def add_close_button(self):
        """Add a close button to the main box."""
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, halign=Gtk.Align.CENTER)
        button_box.set_margin_top(20)
        button_box.set_margin_bottom(20)
        
        close_btn = Gtk.Button(label=_("Close"))
        close_btn.add_css_class("pill")
        close_btn.connect("clicked", lambda b: self.close())
        button_box.append(close_btn)
        
        self.main_box.append(button_box)

    def show_report_view(self):
        # Clear main box
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_content(self.main_box)
        
        # Header Bar with Icon
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(True)
        
        # Add icon to header based on action
        if self.action == "start":
            header_icon = Gtk.Image.new_from_icon_name("input-gaming-symbolic")
        else:
            header_icon = Gtk.Image.new_from_icon_name("user-desktop-symbolic")
        header_icon.set_pixel_size(24)
        header.pack_start(header_icon)
        
        self.main_box.append(header)
        
        # Scrolled Window
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.main_box.append(scroll)
        
        # Content Box
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        content_box.set_margin_start(12)
        content_box.set_margin_end(12)
        content_box.set_margin_top(12)
        content_box.set_margin_bottom(12)
        scroll.set_child(content_box)

        # === APPLIED CHANGES GROUP ===
        changes_group = Adw.PreferencesGroup()
        if self.action == "start":
            changes_group.set_title(_("Applied Optimizations"))
            changes_group.set_description(_("The following changes were applied to your system"))
        else:
            changes_group.set_title(_("Restored Settings"))
            changes_group.set_description(_("The following settings were restored"))
        content_box.append(changes_group)
        
        # Helper to create report row
        def create_report_row(title, subtitle, icon, value_suffix=None):
            row = Adw.ActionRow()
            row.set_title(title)
            row.set_subtitle(subtitle)
            row.add_prefix(Gtk.Image.new_from_icon_name(icon))
            
            if value_suffix:
                value_label = Gtk.Label(label=value_suffix)
                value_label.add_css_class("dim-label")
                value_label.set_valign(Gtk.Align.CENTER)
                row.add_suffix(value_label)
            
            return row
        
        # Add rows based on action
        if self.action == "start":
            changes_group.add(create_report_row(
                _("GameMode Daemon"),
                _("System-wide performance daemon"),
                "input-gaming-symbolic",
                _("Active")
            ))
            changes_group.add(create_report_row(
                _("Visual Effects"),
                _("All KWin effects disabled"),
                "preferences-desktop-effects-symbolic",
                _("OFF")
            ))
            changes_group.add(create_report_row(
                _("Compositor"),
                _("Low latency, tearing allowed, animations = 0"),
                "preferences-desktop-display-symbolic",
                _("Performance")
            ))
            changes_group.add(create_report_row(
                _("GPU Maximum Performance"),
                _("Force maximum performance mode (NVIDIA/AMD)"),
                "application-x-addon-symbolic",
                _("Max Perf")
            ))
            changes_group.add(create_report_row(
                _("Baloo Indexer"),
                _("File indexing suspended"),
                "system-search-symbolic",
                _("Suspended")
            ))
            changes_group.add(create_report_row(
                _("Akonadi Server"),
                _("PIM storage service stopped"),
                "x-office-address-book-symbolic",
                _("Stopped")
            ))
            changes_group.add(create_report_row(
                _("S.M.A.R.T Monitor"),
                _("Disk health monitoring unloaded"),
                "drive-harddisk-symbolic",
                _("Unloaded")
            ))
        else:
            changes_group.add(create_report_row(
                _("GameMode Daemon"),
                _("System-wide performance daemon"),
                "input-gaming-symbolic",
                _("Inactive")
            ))
            changes_group.add(create_report_row(
                _("Visual Effects"),
                _("All KWin effects restored"),
                "preferences-desktop-effects-symbolic",
                _("ON")
            ))
            changes_group.add(create_report_row(
                _("Compositor"),
                _("Balanced latency, animations restored"),
                "preferences-desktop-display-symbolic",
                _("Balanced")
            ))
            changes_group.add(create_report_row(
                _("GPU Maximum Performance"),
                _("Restored to auto/balanced mode"),
                "application-x-addon-symbolic",
                _("Auto")
            ))
            changes_group.add(create_report_row(
                _("Baloo Indexer"),
                _("File indexing resumed"),
                "system-search-symbolic",
                _("Active")
            ))
            changes_group.add(create_report_row(
                _("Akonadi Server"),
                _("PIM storage service restored"),
                "x-office-address-book-symbolic",
                _("Restored")
            ))
            changes_group.add(create_report_row(
                _("S.M.A.R.T Monitor"),
                _("Disk health monitoring restored"),
                "drive-harddisk-symbolic",
                _("Active")
            ))



        # === ACTION BUTTONS ===
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12, halign=Gtk.Align.CENTER)
        button_box.set_margin_top(20)
        button_box.set_margin_bottom(20)
        
        # Steam Games Button (Only on Start)
        if self.action == "start":
            btn_steam = Gtk.Button(label=_("Configure Steam Games"))
            btn_steam.add_css_class("pill")
            btn_steam.connect("clicked", self.on_steam_config)
            button_box.append(btn_steam)

        # Close Button
        btn = Gtk.Button(label=_("Close"))
        btn.add_css_class("pill")
        btn.connect("clicked", self.on_close)
        button_box.append(btn)
        
        self.main_box.append(button_box)

    def on_steam_config(self, btn):
        try:
            try:
                from .steam_games_dialog import SteamGamesDialog
            except ImportError:
                import sys
                import os
                current_dir = os.path.dirname(os.path.abspath(__file__))
                if current_dir not in sys.path:
                    sys.path.append(current_dir)
                import steam_games_dialog
                SteamGamesDialog = steam_games_dialog.SteamGamesDialog

            dlg = SteamGamesDialog(parent=self)
            dlg.present()
        except Exception as e:
            # Handle case where vdf or module is missing or other errors
            d = Adw.MessageDialog(heading="Error", body=f"Cannot load Steam configuration tool: {e}")
            d.add_response("ok", "OK")
            d.set_transient_for(self)
            d.present()

    def on_close(self, btn):
        self.close()
