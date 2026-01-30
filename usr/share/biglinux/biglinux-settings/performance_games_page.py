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
    """Represents a Steam game with its configuration."""
    def __init__(self, app_id, name, launch_options=""):
        self.app_id = app_id
        self.name = name
        self.launch_options = launch_options
        self.has_gamemode = "gamemoderun" in launch_options.lower()


class SteamGamesDialog(Adw.Window):
    """Dialog for configuring Steam games with gamemoderun."""

    def __init__(self, parent_window, **kwargs):
        super().__init__(**kwargs)

        self.set_title(_("Configure Steam Games"))
        self.set_default_size(600, 500)
        self.set_modal(True)
        self.set_transient_for(parent_window)

        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_content(main_box)

        # Header bar
        header = Adw.HeaderBar()
        main_box.append(header)

        # Middle content area (scrollable)
        content_clamp = Adw.Clamp()
        content_clamp.set_maximum_size(800)
        content_clamp.set_vexpand(True)
        main_box.append(content_clamp)

        # Scroll container for games list
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        content_clamp.set_child(scroll)

        # Inner box for scrollable content
        self.inner_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.inner_box.set_margin_top(20)
        self.inner_box.set_margin_bottom(20)
        self.inner_box.set_margin_start(20)
        self.inner_box.set_margin_end(20)
        scroll.set_child(self.inner_box)

        # Fixed footer for buttons (outside scroll)
        self.footer_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.footer_box.set_halign(Gtk.Align.CENTER)
        self.footer_box.set_margin_top(12)
        self.footer_box.set_margin_bottom(12)
        self.footer_box.set_margin_start(20)
        self.footer_box.set_margin_end(20)
        main_box.append(self.footer_box)

        # Check if VDF module is available
        if not VDF_AVAILABLE:
            self._show_vdf_error()
            return

        # Find Steam config
        self.steam_path = self._find_steam_path()
        if not self.steam_path:
            self._show_no_steam_error()
            return

        # Load and display games
        self.games = self._load_steam_games()
        if not self.games:
            self._show_no_games_error()
            return

        self._create_games_list()

    def _find_steam_path(self):
        """Find the Steam installation directory."""
        possible_paths = [
            os.path.expanduser("~/.steam/steam"),
            os.path.expanduser("~/.local/share/Steam"),
            os.path.expanduser("~/.steam/debian-installation"),
        ]

        for path in possible_paths:
            config_file = os.path.join(path, "config", "config.vdf")
            if os.path.exists(config_file):
                return path

        return None

    def _load_steam_games(self):
        """Load installed Steam games and their launch options."""
        games = []
        self.localconfig_path = None

        # Get user ID
        loginusers_path = os.path.join(self.steam_path, "config", "loginusers.vdf")
        user_id = None

        if os.path.exists(loginusers_path):
            try:
                with open(loginusers_path, 'r', encoding='utf-8') as f:
                    data = vdf.load(f)
                    users = data.get("users", {})
                    for steam_id, user_data in users.items():
                        if user_data.get("MostRecent") == "1":
                            user_id = steam_id
                            break
                    if not user_id and users:
                        user_id = list(users.keys())[0]
            except Exception as e:
                print(f"Error reading loginusers.vdf: {e}")

        # Load local config for launch options
        localconfig_dir = os.path.join(self.steam_path, "userdata")
        launch_options = {}

        if os.path.exists(localconfig_dir):
            for folder in os.listdir(localconfig_dir):
                user_config = os.path.join(localconfig_dir, folder, "config", "localconfig.vdf")
                if os.path.exists(user_config):
                    try:
                        with open(user_config, 'r', encoding='utf-8') as f:
                            data = vdf.load(f)
                            apps = data.get("UserLocalConfigStore", {}).get("Software", {}).get("Valve", {}).get("Steam", {}).get("apps", {})
                            for app_id, app_data in apps.items():
                                if isinstance(app_data, dict):
                                    launch_opts = app_data.get("LaunchOptions", "")
                                    launch_options[app_id] = launch_opts
                        self.localconfig_path = user_config
                        break
                    except Exception as e:
                        print(f"Error reading localconfig.vdf: {e}")

        # Load installed games from libraryfolders.vdf
        libraryfolders_path = os.path.join(self.steam_path, "steamapps", "libraryfolders.vdf")
        if os.path.exists(libraryfolders_path):
            try:
                with open(libraryfolders_path, 'r', encoding='utf-8') as f:
                    data = vdf.load(f)
                    folders = data.get("libraryfolders", {})
                    for folder_id, folder_data in folders.items():
                        if isinstance(folder_data, dict) and "apps" in folder_data:
                            for app_id in folder_data["apps"].keys():
                                folder_path = folder_data.get("path", self.steam_path)
                                manifest_path = os.path.join(folder_path, "steamapps", f"appmanifest_{app_id}.acf")
                                if os.path.exists(manifest_path):
                                    try:
                                        with open(manifest_path, 'r', encoding='utf-8') as mf:
                                            manifest = vdf.load(mf)
                                            app_state = manifest.get("AppState", {})
                                            name = app_state.get("name", f"App {app_id}")
                                            
                                            # Filter out non-game items (tools, runtimes, redistributables)
                                            if self._is_game(name, app_id):
                                                launch_opts = launch_options.get(app_id, "")
                                                games.append(SteamGame(app_id, name, launch_opts))
                                    except Exception as e:
                                        print(f"Error reading manifest {app_id}: {e}")
            except Exception as e:
                print(f"Error reading libraryfolders.vdf: {e}")

        games.sort(key=lambda g: g.name.lower())
        return games

    def _is_game(self, name, app_id):
        """Check if the app is an actual game (not a tool, runtime, or redistributable)."""
        name_lower = name.lower()
        
        # Keywords that indicate non-game items
        exclude_keywords = [
            "proton",
            "steam linux runtime",
            "steamworks",
            "redistributable",
            "redist",
            "directx",
            "vcredist",
            "microsoft visual c++",
            "physx",
            "openal",
            ".net",
            "easyanticheat",
            "battleye",
            "steam client",
            "steamvr",
            "steam controller",
            "wallpaper engine",
            "dedicated server",
            "sdk",
            "soldier",
            "sniper",
            "scout",  # Steam runtime codenames
            "pressure-vessel",
        ]
        
        for keyword in exclude_keywords:
            if keyword in name_lower:
                return False
        
        # Known tool App IDs (common Steam tools)
        tool_app_ids = [
            "228980",   # Steamworks Common Redistributables
            "1070560",  # Steam Linux Runtime
            "1391110",  # Steam Linux Runtime - Soldier
            "1628350",  # Steam Linux Runtime - Sniper
            "1493710",  # Proton Experimental
            "2180100",  # Proton Hotfix
            "961940",   # Proton 3.16 Beta
            "1054830",  # Proton 4.2
            "1113280",  # Proton 4.11
            "1245040",  # Proton 5.0
            "1420170",  # Proton 5.13
            "1580130",  # Proton 6.3
            "1887720",  # Proton 7.0
            "2348590",  # Proton 8.0
            "2805730",  # Proton 9.0
            "250820",   # SteamVR
            "1826330",  # Steam Linux Runtime - Scout
        ]
        
        if app_id in tool_app_ids:
            return False
        
        return True

    def _create_games_list(self):
        """Create the games list UI."""
        # Games group (scrollable)
        self.games_group = Adw.PreferencesGroup()
        self.games_group.set_title(_("Installed Games"))
        self.games_group.set_description(_("{} games found").format(len(self.games)))
        self.inner_box.append(self.games_group)

        self.game_checkboxes = {}

        for game in self.games:
            row = Adw.ActionRow()
            row.set_title(game.name)
            row.set_subtitle(f"App ID: {game.app_id}")

            check = Gtk.CheckButton()
            check.set_active(game.has_gamemode)
            check.set_valign(Gtk.Align.CENTER)
            check.connect("toggled", self._on_game_toggled, game)
            row.add_suffix(check)
            row.set_activatable_widget(check)

            self.game_checkboxes[game.app_id] = check
            self.games_group.add(row)

        # Fixed footer buttons
        select_all_btn = Gtk.Button(label=_("Select All"))
        select_all_btn.connect("clicked", self._on_select_all)
        self.footer_box.append(select_all_btn)

        deselect_all_btn = Gtk.Button(label=_("Deselect All"))
        deselect_all_btn.connect("clicked", self._on_deselect_all)
        self.footer_box.append(deselect_all_btn)

        # Spacer
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        self.footer_box.append(spacer)

        apply_btn = Gtk.Button(label=_("Apply Changes"))
        apply_btn.add_css_class("suggested-action")
        apply_btn.connect("clicked", self._on_apply)
        self.footer_box.append(apply_btn)

        close_btn = Gtk.Button(label=_("Close"))
        close_btn.connect("clicked", lambda b: self.close())
        self.footer_box.append(close_btn)

    def _on_select_all(self, button):
        for check in self.game_checkboxes.values():
            check.set_active(True)

    def _on_deselect_all(self, button):
        for check in self.game_checkboxes.values():
            check.set_active(False)

    def _on_game_toggled(self, check, game):
        game.has_gamemode = check.get_active()

    def _on_apply(self, button):
        if not self.localconfig_path or not os.path.exists(self.localconfig_path):
            self._show_error(_("Could not find Steam configuration file"))
            return

        try:
            with open(self.localconfig_path, 'r', encoding='utf-8') as f:
                data = vdf.load(f)

            apps = data.setdefault("UserLocalConfigStore", {}).setdefault("Software", {}).setdefault("Valve", {}).setdefault("Steam", {}).setdefault("apps", {})

            for game in self.games:
                app_data = apps.setdefault(game.app_id, {})
                current_opts = app_data.get("LaunchOptions", "")

                new_opts = re.sub(r'gamemoderun\s*%command%\s*', '', current_opts).strip()

                if game.has_gamemode:
                    if "gamemoderun" not in new_opts.lower():
                        new_opts = f"gamemoderun %command% {new_opts}".strip()

                if new_opts:
                    app_data["LaunchOptions"] = new_opts
                elif "LaunchOptions" in app_data:
                    del app_data["LaunchOptions"]

            # Backup original file
            backup_path = self.localconfig_path + ".backup"
            if not os.path.exists(backup_path):
                import shutil
                shutil.copy2(self.localconfig_path, backup_path)

            with open(self.localconfig_path, 'w', encoding='utf-8') as f:
                vdf.dump(data, f, pretty=True)

            self._show_success(_("Changes applied successfully! Restart Steam to see the changes."))

        except Exception as e:
            self._show_error(_("Failed to apply changes: {}").format(str(e)))

    def _show_vdf_error(self):
        status = Adw.StatusPage()
        status.set_icon_name("dialog-error-symbolic")
        status.set_title(_("Module Not Found"))
        status.set_description(_("The 'vdf' Python module is required. Install it with:\npip install vdf"))
        self.inner_box.append(status)

    def _show_no_steam_error(self):
        status = Adw.StatusPage()
        status.set_icon_name("dialog-error-symbolic")
        status.set_title(_("Steam Not Found"))
        status.set_description(_("Could not find Steam installation. Make sure Steam is installed."))
        self.inner_box.append(status)

    def _show_no_games_error(self):
        status = Adw.StatusPage()
        status.set_icon_name("dialog-information-symbolic")
        status.set_title(_("No Games Found"))
        status.set_description(_("No Steam games were found."))
        self.inner_box.append(status)

    def _show_error(self, message):
        dialog = Adw.MessageDialog.new(self, _("Error"), message)
        dialog.add_response("ok", _("OK"))
        dialog.present()

    def _show_success(self, message):
        dialog = Adw.MessageDialog.new(self, _("Success"), message)
        dialog.add_response("ok", _("OK"))
        dialog.present()


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
