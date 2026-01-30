from base_page import BaseSettingsPage, _, ICONS_DIR
import os
import gi
import json
import subprocess
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk, Gio, GLib

class SteamGamesDialog(Adw.Window):
    """Dialog for configuring Steam games via shell script."""
    
    def __init__(self, parent_window, **kwargs):
        super().__init__(**kwargs)
        self.set_title(_("Configure Steam Games"))
        self.set_default_size(600, 500)
        self.set_modal(True)
        self.set_transient_for(parent_window)
        
        self.script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "perf_games", "configureSteam.sh")
        self.game_checkboxes = {}
        self.games = []

        # Build UI
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)
        
        # HeaderBar with Steam icon
        header = Adw.HeaderBar()
        steam_icon_path = os.path.join(ICONS_DIR, "steam-symbolic.svg")
        steam_gfile = Gio.File.new_for_path(steam_icon_path)
        steam_icon = Gio.FileIcon.new(steam_gfile)
        steam_img = Gtk.Image.new_from_gicon(steam_icon)
        steam_img.set_pixel_size(24)
        steam_img.add_css_class("symbolic-icon")
        header.pack_start(steam_img)
        main_box.append(header)

        # Scrollable content
        clamp = Adw.Clamp(maximum_size=800, vexpand=True)
        main_box.append(clamp)
        scroll = Gtk.ScrolledWindow(vexpand=True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        clamp.set_child(scroll)
        self.inner_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20,
                                  margin_top=20, margin_bottom=20, margin_start=20, margin_end=20)
        scroll.set_child(self.inner_box)

        # Footer
        self.footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, halign=Gtk.Align.CENTER,
                              margin_top=12, margin_bottom=12, margin_start=20, margin_end=20)
        main_box.append(self.footer)

        self._load_data()

    def _load_data(self):
        # Load from script
        try:
            result = subprocess.run([self.script_path, "list"], capture_output=True, text=True)
            if result.returncode != 0:
                self._show_status("dialog-error-symbolic", _("Error"), _("Failed to load games list."))
                print(result.stderr)
                return

            try:
                data = json.loads(result.stdout)
            except json.JSONDecodeError:
                self._show_status("dialog-error-symbolic", _("Error"), _("Invalid data received."))
                return

            if isinstance(data, dict) and "error" in data:
                 self._show_status("dialog-error-symbolic", _("Error"), data["error"])
                 return
            
            self.games = data
            if not self.games:
                self._show_status("dialog-information-symbolic", _("No Games Found"), _("No Steam games found."))
                return
                
            self._create_games_list()
            
        except Exception as e:
            self._show_status("dialog-error-symbolic", _("Error"), str(e))

    def _create_games_list(self):
        group = Adw.PreferencesGroup(title=_("Installed Games"), description=_("{} games found").format(len(self.games)))
        self.inner_box.append(group)

        for game in self.games:
            game_name = game.get("name", "Unknown")
            app_id = game.get("app_id", "")
            has_gamemode = game.get("has_gamemode", False)
            
            row = Adw.ActionRow(title=game_name, subtitle=f"App ID: {app_id}")
            check = Gtk.CheckButton(active=has_gamemode, valign=Gtk.Align.CENTER)
            
            # We need to update our local list/dict when toggled
            check.connect("toggled", self._on_toggled, game)
            
            row.add_suffix(check)
            row.set_activatable_widget(check)
            self.game_checkboxes[app_id] = check
            group.add(row)

        # Footer buttons
        for label, callback in [(_("Select All"), lambda b: [c.set_active(True) for c in self.game_checkboxes.values()]),
                                (_("Deselect All"), lambda b: [c.set_active(False) for c in self.game_checkboxes.values()])]:
            btn = Gtk.Button(label=label)
            btn.connect("clicked", callback)
            self.footer.append(btn)
        
        spacer = Gtk.Box(hexpand=True)
        self.footer.append(spacer)
        
        apply_btn = Gtk.Button(label=_("Apply Changes"))
        apply_btn.add_css_class("suggested-action")
        apply_btn.connect("clicked", self._on_apply)
        self.footer.append(apply_btn)
        
        close_btn = Gtk.Button(label=_("Close"))
        close_btn.connect("clicked", lambda b: self.close())
        self.footer.append(close_btn)

    def _on_toggled(self, button, game_dict):
        game_dict["has_gamemode"] = button.get_active()

    def _on_apply(self, button):
        # Show confirmation dialog
        dlg = Adw.MessageDialog.new(
            self,
            _("Close Steam?"),
            _("Steam must be closed for changes to be applied. If Steam is running, the modifications will not take effect.")
        )
        dlg.add_response("cancel", _("Cancel"))
        dlg.add_response("close_steam", _("Close Steam and Apply"))
        dlg.set_response_appearance("close_steam", Adw.ResponseAppearance.SUGGESTED)
        dlg.set_default_response("close_steam")
        dlg.connect("response", self._on_confirm_response)
        dlg.present()

    def _on_confirm_response(self, dialog, response):
        if response != "close_steam":
            return
        
        # Call script to close steam
        subprocess.run([self.script_path, "close_steam"], capture_output=True)
        
        # Start checking if Steam is closed
        self._steam_check_count = 0
        self._max_checks = 10 
        GLib.timeout_add(500, self._check_steam_closed)

    def _check_steam_closed(self):
        self._steam_check_count += 1
        
        res = subprocess.run([self.script_path, "check_steam"], capture_output=True, text=True)
        status = res.stdout.strip()
        
        if status == "running":
            if self._steam_check_count < self._max_checks:
                # Try killing again
                subprocess.run([self.script_path, "close_steam"], capture_output=True)
                return True  # Continue checking
            else:
                self._show_msg(_("Error"), _("Could not close Steam. Please close it manually and try again."))
                return False 
        
        # Steam is closed, apply changes
        self._apply_changes()
        return False

    def _apply_changes(self):
        # Collect enabled IDs
        enabled_ids = [g["app_id"] for g in self.games if g["has_gamemode"]]
        args_str = " ".join(enabled_ids)
        
        try:
            res = subprocess.run([self.script_path, "apply", args_str], capture_output=True, text=True)
            if res.returncode == 0:
                success_dlg = Adw.MessageDialog.new(self, _("Success"), _("Changes applied successfully!"))
                success_dlg.add_response("ok", _("OK"))
                success_dlg.connect("response", lambda d, r: self.close())
                success_dlg.present()
            else:
                self._show_msg(_("Error"), f"Script failed: {res.stderr}")
        except Exception as e:
            self._show_msg(_("Error"), str(e))

    def _show_status(self, icon, title, desc):
        status = Adw.StatusPage(icon_name=icon, title=title, description=desc)
        self.inner_box.append(status)

    def _show_msg(self, title, msg):
        dlg = Adw.MessageDialog.new(self, title, msg)
        dlg.add_response("ok", _("OK"))
        dlg.present()


class PerformanceGamesPage(BaseSettingsPage):
    def __init__(self, main_window, **kwargs):
        super().__init__(main_window, **kwargs)

        # Create the container (base method)
        content = self.create_scrolled_content()

        ## GROUP ##

        # Performance
        performance_group = self.create_group(
            _("Performance"), _("BigLinux performance tweaks."), "perf_games"
        )
        content.append(performance_group)

        # Games
        games_group = self.create_group(
            _("Games Booster"),
            _("Combination of daemon and library that allows games to request a set of optimizations be temporarily applied to the operating system and/or the game process."),
            "perf_games",
        )
        content.append(games_group)

        ## Performance ##
        # Disable Visual Effects
        self.create_row(
            performance_group,
            _("Disable Visual Effects"),
            _("Disables KWin visual effects (blur, shadows, animations). Reduces GPU load and frees memory."),
            "disableVisualEffects",
            "disable-visual-effects-symbolic",
        )
        # Compositor Settings
        self.create_row(
            performance_group,
            _("Compositor Settings"),
            _("Configures compositor for low latency, allows tearing and disables animations. Minimizes compositing overhead and reduces input lag."),
            "compositorSettings",
            "compositor-settings-symbolic",
        )
        # CPU Maximum Performance
        self.create_row(
            performance_group,
            _("CPU Maximum Performance"),
            _("Forces maximum processor performance mode. Ensures the processor uses maximum frequency."),
            "cpuMaximumPerformance",
            "cpu-maximum-performance-symbolic",
        )
        # GPU Maximum Performance
        self.create_row(
            performance_group,
            _("GPU Maximum Performance"),
            _("Forces maximum GPU performance mode (NVIDIA/AMD). Ensures the graphics card uses maximum frequency."),
            "gpuMaximumPerformance",
            "gpu-maximum-performance-symbolic",
        )
        # Disable Baloo Indexer
        self.create_row(
            performance_group,
            _("Disable Baloo Indexer"),
            _("Disables the Baloo file indexer. Avoids disk I/O overhead."),
            "disableBalooIndexer",
            "disable-baloo-indexer-symbolic",
        )
        # Stop Akonadi Server
        self.create_row(
            performance_group,
            _("Stop Akonadi Server"),
            _("Stops the PIM data server (Kontact/Thunderbird). Reduces memory and disk overhead."),
            "stopAkonadiServer",
            "stop-akonadi-server-symbolic",
        )
        # Unload S.M.A.R.T Monitor
        smart = self.create_row(
            performance_group,
            _("Unload S.M.A.R.T Monitor"),
            _("Disables S.M.A.R.T disk monitoring. Reduces disk I/O and CPU usage."),
            "unloadSmartMonitor",
            "unload-smart-monitor-symbolic",
        )

        ## GAMES ##
        # GameMode Daemon
        # Using Adw.ExpanderRow to allow extra configuration for Steam
        row = Adw.ExpanderRow()
        row.set_title(_("GameMode Daemon"))
        row.set_subtitle(_("Activates daemon that adjusts CPU, I/O, etc. Reduces latency and increases frame rate."))
        
        # Icon
        icon_name = "gamemode-daemon-symbolic"
        icon_path = os.path.join(ICONS_DIR, f"{icon_name}.svg")
        gfile = Gio.File.new_for_path(icon_path)
        icon = Gio.FileIcon.new(gfile)
        img = Gtk.Image.new_from_gicon(icon)
        img.set_pixel_size(24)
        img.add_css_class("symbolic-icon")
        row.add_prefix(img)

        # Switch
        switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        row.add_suffix(switch)
        
        # Script association
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "perf_games", "gamemodeDaemon.sh")
        self.switch_scripts[switch] = script_path
        switch.connect("state-set", self.on_switch_changed)
        
        # Enable expansion only when switch is active
        def on_daemon_toggled(sw, _pspec):
            active = sw.get_active()
            row.set_enable_expansion(active)
            if not active:
                row.set_expanded(False)
        
        switch.connect("notify::active", on_daemon_toggled)
        # Initial state wlll be set by sync_all_switches, but we set a default here
        row.set_enable_expansion(False)

        # Configure Steam Option
        steam_row = Adw.ActionRow()
        steam_row.set_title(_("Configure Steam"))
        steam_row.set_subtitle(_("Select games to enable 'gamemoderun %command%' launch option."))
        
        # Steam icon
        steam_icon_path = os.path.join(ICONS_DIR, "steam-symbolic.svg")
        steam_gfile = Gio.File.new_for_path(steam_icon_path)
        steam_icon = Gio.FileIcon.new(steam_gfile)
        steam_img = Gtk.Image.new_from_gicon(steam_icon)
        steam_img.set_pixel_size(20)
        steam_img.add_css_class("symbolic-icon")
        steam_row.add_prefix(steam_img)
        
        open_btn = Gtk.Button(label=_("Open"), valign=Gtk.Align.CENTER)
        open_btn.connect("clicked", lambda b: SteamGamesDialog(self.main_window).present())
        
        steam_row.add_suffix(open_btn)
        row.add_row(steam_row)
        
        games_group.add(row)

        self.sync_all_switches()
