import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

import os
import re

from gi.repository import Adw, Gtk, Gio
from base_page import BaseSettingsPage, _

# Try to import vdf module for Steam config parsing
try:
    import vdf
    VDF_AVAILABLE = True
except ImportError:
    VDF_AVAILABLE = False


class SteamGame:
    """Represents a Steam game."""
    def __init__(self, app_id, name, launch_options=""):
        self.app_id, self.name, self.launch_options = app_id, name, launch_options
        self.has_gamemode = "gamemoderun" in launch_options.lower()


class SteamGamesDialog(Adw.Window):
    """Dialog for configuring Steam games with gamemoderun."""
    
    # Keywords and IDs to filter out non-game items
    EXCLUDE_KEYWORDS = ["proton", "steam linux runtime", "steamworks", "redistributable", "redist",
                        "directx", "vcredist", "visual c++", "physx", "openal", ".net", "easyanticheat",
                        "battleye", "steam client", "steamvr", "steam controller", "dedicated server",
                        "sdk", "soldier", "sniper", "scout", "pressure-vessel"]
    EXCLUDE_IDS = {"228980", "1070560", "1391110", "1628350", "1493710", "2180100", "961940", "1054830",
                   "1113280", "1245040", "1420170", "1580130", "1887720", "2348590", "2805730", "250820", "1826330"}

    def __init__(self, parent_window, **kwargs):
        super().__init__(**kwargs)
        self.set_title(_("Configure Steam Games"))
        self.set_default_size(600, 500)
        self.set_modal(True)
        self.set_transient_for(parent_window)
        self.localconfig_path = None
        self.game_checkboxes = {}

        # Build UI
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)
        main_box.append(Adw.HeaderBar())

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

        # Load data
        if not VDF_AVAILABLE:
            self._show_status("dialog-error-symbolic", _("Module Not Found"), _("Install 'vdf': pip install vdf"))
            return
        self.steam_path = self._find_steam_path()
        if not self.steam_path:
            self._show_status("dialog-error-symbolic", _("Steam Not Found"), _("Steam installation not found."))
            return
        self.games = self._load_steam_games()
        if not self.games:
            self._show_status("dialog-information-symbolic", _("No Games Found"), _("No Steam games found."))
            return
        self._create_games_list()

    def _find_steam_path(self):
        for path in ["~/.steam/steam", "~/.local/share/Steam", "~/.steam/debian-installation"]:
            full = os.path.expanduser(path)
            if os.path.exists(os.path.join(full, "config", "config.vdf")):
                return full
        return None

    def _load_steam_games(self):
        games, launch_options = [], {}
        
        # Load launch options from userdata
        userdata = os.path.join(self.steam_path, "userdata")
        if os.path.exists(userdata):
            for folder in os.listdir(userdata):
                cfg = os.path.join(userdata, folder, "config", "localconfig.vdf")
                if os.path.exists(cfg):
                    try:
                        with open(cfg, 'r', encoding='utf-8') as f:
                            apps = vdf.load(f).get("UserLocalConfigStore", {}).get("Software", {}).get("Valve", {}).get("Steam", {}).get("apps", {})
                            launch_options = {k: v.get("LaunchOptions", "") for k, v in apps.items() if isinstance(v, dict)}
                        self.localconfig_path = cfg
                        break
                    except: pass

        # Load games from library
        libfolders = os.path.join(self.steam_path, "steamapps", "libraryfolders.vdf")
        if os.path.exists(libfolders):
            try:
                with open(libfolders, 'r', encoding='utf-8') as f:
                    for fdata in vdf.load(f).get("libraryfolders", {}).values():
                        if isinstance(fdata, dict) and "apps" in fdata:
                            for app_id in fdata["apps"]:
                                manifest = os.path.join(fdata.get("path", self.steam_path), "steamapps", f"appmanifest_{app_id}.acf")
                                if os.path.exists(manifest):
                                    try:
                                        with open(manifest, 'r', encoding='utf-8') as mf:
                                            name = vdf.load(mf).get("AppState", {}).get("name", f"App {app_id}")
                                            if self._is_game(name, app_id):
                                                games.append(SteamGame(app_id, name, launch_options.get(app_id, "")))
                                    except: pass
            except: pass
        return sorted(games, key=lambda g: g.name.lower())

    def _is_game(self, name, app_id):
        name_lower = name.lower()
        return app_id not in self.EXCLUDE_IDS and not any(k in name_lower for k in self.EXCLUDE_KEYWORDS)

    def _create_games_list(self):
        group = Adw.PreferencesGroup(title=_("Installed Games"), description=_("{} games found").format(len(self.games)))
        self.inner_box.append(group)

        for game in self.games:
            row = Adw.ActionRow(title=game.name, subtitle=f"App ID: {game.app_id}")
            check = Gtk.CheckButton(active=game.has_gamemode, valign=Gtk.Align.CENTER)
            check.connect("toggled", lambda c, g: setattr(g, 'has_gamemode', c.get_active()), game)
            row.add_suffix(check)
            row.set_activatable_widget(check)
            self.game_checkboxes[game.app_id] = check
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

    def _on_apply(self, button):
        if not self.localconfig_path or not os.path.exists(self.localconfig_path):
            return self._show_msg(_("Error"), _("Steam config not found"))
        
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
        
        import subprocess
        from gi.repository import GLib
        
        # Kill Steam processes
        subprocess.run(["pkill", "-9", "steam"], capture_output=True)
        subprocess.run(["pkill", "-9", "steamwebhelper"], capture_output=True)
        
        # Start checking if Steam is closed
        self._steam_check_count = 0
        self._max_checks = 10  # 10 checks * 500ms = 5 seconds max wait
        GLib.timeout_add(500, self._check_steam_closed)

    def _is_steam_running(self):
        import subprocess
        result = subprocess.run(["pgrep", "-f", "steam"], capture_output=True)
        return result.returncode == 0

    def _check_steam_closed(self):
        from gi.repository import GLib
        
        self._steam_check_count += 1
        
        if self._is_steam_running():
            if self._steam_check_count < self._max_checks:
                # Steam still running, try killing again and check later
                import subprocess
                subprocess.run(["pkill", "-9", "steam"], capture_output=True)
                subprocess.run(["pkill", "-9", "steamwebhelper"], capture_output=True)
                return True  # Continue checking
            else:
                # Max retries reached, show error
                self._show_msg(_("Error"), _("Could not close Steam. Please close it manually and try again."))
                return False  # Stop checking
        
        # Steam is closed, apply changes
        self._apply_changes()
        return False  # Stop checking

    def _apply_changes(self):
        try:
            with open(self.localconfig_path, 'r', encoding='utf-8') as f:
                data = vdf.load(f)
            apps = data.setdefault("UserLocalConfigStore", {}).setdefault("Software", {}).setdefault("Valve", {}).setdefault("Steam", {}).setdefault("apps", {})
            
            for game in self.games:
                app = apps.setdefault(game.app_id, {})
                opts = re.sub(r'gamemoderun\s*%command%\s*', '', app.get("LaunchOptions", "")).strip()
                if game.has_gamemode and "gamemoderun" not in opts.lower():
                    opts = f"gamemoderun %command% {opts}".strip()
                if opts:
                    app["LaunchOptions"] = opts
                elif "LaunchOptions" in app:
                    del app["LaunchOptions"]

            # Backup and save
            backup = self.localconfig_path + ".backup"
            if not os.path.exists(backup):
                import shutil
                shutil.copy2(self.localconfig_path, backup)
            with open(self.localconfig_path, 'w', encoding='utf-8') as f:
                vdf.dump(data, f, pretty=True)
            
            # Show success and close dialog
            success_dlg = Adw.MessageDialog.new(self, _("Success"), _("Changes applied successfully!"))
            success_dlg.add_response("ok", _("OK"))
            success_dlg.connect("response", lambda d, r: self.close())
            success_dlg.present()
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
            _(
                "Combination of daemon and library that allows games to request a set of optimizations be temporarily applied to the operating system and/or the game process."
            ),
            "perf_games",
        )
        content.append(games_group)

        ## Performance ##
        # Disable Visual Effects
        self.create_row(
            performance_group,
            _("Disable Visual Effects"),
            _(
                "Disables KWin visual effects (blur, shadows, animations). Reduces GPU load and frees memory."
            ),
            "disableVisualEffects",
            "disable-visual-effects-symbolic",
        )
        # Compositor Settings
        self.create_row(
            performance_group,
            _("Compositor Settings"),
            _(
                "Configures compositor for low latency, allows tearing and disables animations. Minimizes compositing overhead and reduces input lag."
            ),
            "compositorSettings",
            "compositor-settings-symbolic",
        )
        # CPU Maximum Performance
        self.create_row(
            performance_group,
            _("CPU Maximum Performance"),
            _(
                "Forces maximum processor performance mode. Ensures the processor uses maximum frequency."
            ),
            "cpuMaximumPerformance",
            "cpu-maximum-performance-symbolic",
        )
        # GPU Maximum Performance
        self.create_row(
            performance_group,
            _("GPU Maximum Performance"),
            _(
                "Forces maximum GPU performance mode (NVIDIA/AMD). Ensures the graphics card uses maximum frequency."
            ),
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
            _(
                "Stops the PIM data server (Kontact/Thunderbird). Reduces memory and disk overhead."
            ),
            "stopAkonadiServer",
            "stop-akonadi-server-symbolic",
        )
        # Unload S.M.A.R.T Monitor
        self.create_row(
            performance_group,
            _("Unload S.M.A.R.T Monitor"),
            _("Disables S.M.A.R.T disk monitoring. Reduces disk I/O and CPU usage."),
            "unloadSmartMonitor",
            "unload-smart-monitor-symbolic",
        )

        ## GAMES ##
        # Game Mode Daemon - Expander with switch
        gamemode_expander, gameMode = self.create_switch_expander_row(
            games_group,
            _("GameMode Daemon"),
            _(
                "Activates daemon that adjusts CPU, I/O, etc. Reduces latency and increases frame rate."
            ),
            "gamemodeDaemon",
            "gamemode-daemon-symbolic",
        )

        # Add Configure Steam action row inside the expander
        self.add_action_row_to_expander(
            gamemode_expander,
            _("Configure Steam"),
            _("Select games to enable 'gamemoderun %command%' launch option."),
            _("Open"),
            self.on_configure_steam_clicked,
            "steam-symbolic"
        )

        self.sync_all_switches()

    def on_configure_steam_clicked(self, button):
        """Opens the Steam games configuration dialog."""
        dialog = SteamGamesDialog(self.main_window)
        dialog.present()
