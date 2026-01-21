
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
        self.set_default_size(500, 500)
        
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
        threading.Thread(target=self.process_thread).start()

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
             if self.on_close_callback:
                self.on_close_callback(False)
        else:
            self.status_page.set_title(_("Failed"))
            self.status_page.set_description(_("Process failed. Check logs."))
            self.status_page.set_icon_name("dialog-error-symbolic")
            if self.on_close_callback:
                self.on_close_callback(False)

    def show_report_view(self):
        # Clear main box
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_content(self.main_box)
        
        # Status Page for Header
        status_page = Adw.StatusPage()
        
        if self.action == "start":
            status_page.set_title(_("Game Mode Enabled"))
            status_page.set_description(_("System is optimized for gaming."))
            status_page.set_icon_name("input-gaming-symbolic")
        else:
            status_page.set_title(_("Game Mode Disabled"))
            status_page.set_description(_("System restored to desktop mode."))
            status_page.set_icon_name("user-desktop-symbolic")

        self.main_box.append(status_page)

        # Create Preferences Group for Report Items
        group = Adw.PreferencesGroup()
        
        # Parse logic: Look for lines after "SYSTEM STATUS REPORT"
        report_started = False
        for line in self.collected_log:
            if "SYSTEM STATUS REPORT" in line:
                report_started = True
                continue
            if not report_started:
                continue
            if "=====" in line:
                continue
            
            parts = line.split(":", 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                
                # Determine icon based on key
                icon = "preferences-system-details"
                if "CPU" in key: icon = "cpu"
                elif "Swap" in key: icon = "drive-harddisk"
                elif "Compositor" in key: icon = "preferences-desktop-display"
                elif "TCP" in key: icon = "network-transmit-receive"
                elif "GameMode" in key: icon = "input-gaming"

                row = Adw.ActionRow()
                row.set_title(key)
                row.set_subtitle(value)
                row.add_prefix(Gtk.Image.new_from_icon_name(icon))
                group.add(row)

        # Wrap group in clamp
        clamp = Adw.Clamp(maximum_size=500)
        clamp.set_child(group)
        self.main_box.append(clamp)
        
        # Buttons Box
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, halign=Gtk.Align.CENTER, spacing=10, margin_top=20, margin_bottom=20)
        
        # Steam Games Button (Only on Start)
        if self.action == "start":
            btn_steam = Gtk.Button(label=_("Configure Steam Games"))
            btn_steam.add_css_class("pill")
            btn_steam.connect("clicked", self.on_steam_config)
            box.append(btn_steam)

        # Close Button
        btn = Gtk.Button(label=_("Close"))
        btn.add_css_class("pill")
        btn.connect("clicked", self.on_close)
        box.append(btn)
        
        self.main_box.append(box)

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
