from base_page import BaseSettingsPage, _, ICONS_DIR
import os
import gi
import json
import subprocess
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk, Gio, GLib

class GameModeConfigDialog(Adw.Window):
    """Dialog for configuring gamemode.ini options with hardware detection."""
    
    def __init__(self, parent_window, **kwargs):
        super().__init__(**kwargs)
        self.set_title(_("GameMode Configuration"))
        self.set_default_size(600, 600)
        self.set_modal(True)
        self.set_transient_for(parent_window)
        
        self.script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "perf_games", "configureGamemode.sh")
        self.hardware_info = {}
        self.current_config = {}
        self.option_switches = {}
        
        # Build UI
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)
        
        # HeaderBar
        header = Adw.HeaderBar()
        # GameMode icon
        icon_path = os.path.join(ICONS_DIR, "gamemode-daemon-symbolic.svg")
        gfile = Gio.File.new_for_path(icon_path)
        icon = Gio.FileIcon.new(gfile)
        img = Gtk.Image.new_from_gicon(icon)
        img.set_pixel_size(24)
        img.add_css_class("symbolic-icon")
        header.pack_start(img)
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
        
        # Restore Defaults Button
        restore_btn = Gtk.Button(label=_("Restore Defaults"))
        restore_btn.add_css_class("destructive-action")
        restore_btn.connect("clicked", self._on_restore_defaults)
        self.footer.append(restore_btn)
        
        close_btn = Gtk.Button(label=_("Close"))
        close_btn.connect("clicked", lambda b: self.close())
        self.footer.append(close_btn)
        
        self._load_data()
    
    def _parse_shell_output(self, output):
        """Parse key=value pairs from shell script output."""
        data = {}
        for line in output.splitlines():
            line = line.strip()
            if not line or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            
            # Convert boolean strings
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            
            data[key] = value
        return data

    def _load_data(self):
        """Load hardware detection and current config."""
        try:
            # Detect hardware
            result = subprocess.run([self.script_path, "detect"], capture_output=True, text=True)
            if result.returncode == 0:
                self.hardware_info = self._parse_shell_output(result.stdout)
            else:
                self.hardware_info = {}
            
            # Read current config
            result = subprocess.run([self.script_path, "read"], capture_output=True, text=True)
            if result.returncode == 0:
                self.current_config = self._parse_shell_output(result.stdout)
            else:
                self.current_config = {}
            
            self._create_config_ui()
            
        except Exception as e:
            self._show_status("dialog-error-symbolic", _("Error"), str(e))
    
    def _create_config_ui(self):
        """Create the configuration interface with switches."""
        
        # Clear existing children
        child = self.inner_box.get_first_child()
        while child:
            self.inner_box.remove(child)
            child = self.inner_box.get_first_child()
            
        self.option_switches = {} # Reset switches dict
        
        # --- GENERAL SECTION ---
        general_group = Adw.PreferencesGroup(
            title=_("General Settings"),
            description=_("Power governors and platform profiles.")
        )
        self.inner_box.append(general_group)
        
        # Desired Governor
        self._add_option_row(
            general_group,
            "desiredgov",
            _("CPU Governor: Performance"),
            _("Sets the CPU governor to 'performance' when GameMode is active."),
            "performance",
            "powersave"
        )
        
        # Desired Platform Profile
        self._add_option_row(
            general_group,
            "desiredprof",
            _("Platform Profile: Performance"),
            _("Sets the platform profile to 'performance' for maximum power."),
            "performance",
            "balanced"
        )
        
        # iGPU Governor (for hybrid graphics)
        if self.hardware_info.get("has_intel_igpu", False) or self.hardware_info.get("has_amd", False):
            self._add_option_row(
                general_group,
                "igpu_desiredgov",
                _("iGPU Governor: Powersave"),
                _("Sets iGPU governor to powersave when under heavy load to balance power."),
                "powersave",
                "performance"
            )
        
        # --- CPU SECTION ---
        cpu_group = Adw.PreferencesGroup(
            title=_("CPU Optimizations"),
            description=self._get_cpu_description()
        )
        self.inner_box.append(cpu_group)
        
        # Pin Cores
        if self.hardware_info.get("cpu_supports_pin_cores", False):
            self._add_option_row(
                cpu_group,
                "pin_cores",
                _("Pin Cores (P-Cores)"),
                _("Keeps game threads fixed on high-performance cores, preventing the kernel from moving the game to slow cores (E-cores) mid-action."),
                "yes",
                "no"
            )
        
        # Park Cores (only for Intel Hybrid)
        if self.hardware_info.get("cpu_supports_park_cores", False):
            self._add_option_row(
                cpu_group,
                "park_cores",
                _("Park Efficiency Cores"),
                _("Temporarily 'turns off' efficiency cores so the OS doesn't try to use them for the game."),
                "yes",
                "no"
            )
        
        # AMD X3D Mode (for dual CCD X3D CPUs)
        if self.hardware_info.get("supports_amd_x3d_mode", False):
            self._add_option_row(
                cpu_group,
                "amd_x3d_mode_desired",
                _("AMD X3D Mode: Frequency"),
                _("Shifts processes to frequency CCD while gaming. For 7950X3D/9950X3D."),
                "frequency",
                "cache"
            )
        
        # Soft Realtime Scheduling
        self._add_option_row(
            cpu_group,
            "softrealtime",
            _("Soft Realtime Scheduling"),
            _("Enables SCHED_ISO on supported kernels for reduced latency. 'auto' enables with 4+ cores."),
            "auto",
            "off"
        )
        
        # Renice
        self._add_option_row(
            cpu_group,
            "renice",
            _("Renice Game Process"),
            _("Adjusts process priority for the game. Value 10 gives higher priority (requires gamemode group)."),
            "10",
            "0"
        )
        
        # I/O Priority
        self._add_option_row(
            cpu_group,
            "ioprio",
            _("I/O Priority: Maximum"),
            _("Sets I/O priority to BE/0 (highest). Improves disk access for the game."),
            "0",
            "4"
        )
        
        # --- GPU SECTION ---
        gpu_group = Adw.PreferencesGroup(
            title=_("GPU Optimizations"),
            description=self._get_gpu_description()
        )
        self.inner_box.append(gpu_group)
        
        # GPU Optimizations toggle
        self._add_option_row(
            gpu_group,
            "apply_gpu_optimisations",
            _("Enable GPU Optimizations"),
            _("⚠️ Use at your own risk! Enables GPU overclocks and power settings."),
            "accept-responsibility",
            "0"
        )
        
        # NVIDIA Options (X11 Only)
        # These options rely on NV-CONTROL X extension which is not available on Wayland
        is_x11 = self.hardware_info.get("display_server", "") == "x11"
        
        if self.hardware_info.get("has_nvidia", False):
            if is_x11:
                self._add_option_row(
                    gpu_group,
                    "nv_powermizer_mode",
                    _("NVIDIA: Prefer Maximum Performance"),
                    _("Sets GPUPowerMizerMode to 1 (Prefer Maximum Performance). Requires coolbits (X11 Only)."),
                    "1",
                    "0"
                )
                
                self._add_option_row(
                    gpu_group,
                    "nv_core_clock_mhz_offset",
                    _("NVIDIA: Core Clock Offset"),
                    _("Adds MHz offset to core clock. Set to enable +100MHz offset (X11 Only)."),
                    "100",
                    "0"
                )
                
                self._add_option_row(
                    gpu_group,
                    "nv_mem_clock_mhz_offset",
                    _("NVIDIA: Memory Clock Offset"),
                    _("Adds MHz offset to memory clock. Set to enable +200MHz offset (X11 Only)."),
                    "200",
                    "0"
                )
            else:
                # Inform user why options are missing
                warning_row = Adw.ActionRow(title=_("NVIDIA Options Unavailable"))
                warning_row.set_subtitle(_("NVIDIA GameMode optimizations require an X11 session. You are currently using Wayland."))
                warning_img = Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
                warning_img.add_css_class("warning")
                warning_row.add_prefix(warning_img)
                gpu_group.add(warning_row)
        
        # AMD Options
        if self.hardware_info.get("has_amd", False):
            self._add_option_row(
                gpu_group,
                "amd_performance_level",
                _("AMD: High Performance Level"),
                _("Sets power_dpm_force_performance_level to 'high'. Forces max clocks."),
                "high",
                "auto"
            )
        
        # --- SYSTEM SECTION ---
        system_group = Adw.PreferencesGroup(
            title=_("System Settings"),
            description=_("Screen and system-level optimizations.")
        )
        self.inner_box.append(system_group)
        
        # Inhibit Screensaver
        self._add_option_row(
            system_group,
            "inhibit_screensaver",
            _("Inhibit Screensaver"),
            _("Prevents screensaver from activating while GameMode is active."),
            "1",
            "0"
        )
        
        # Disable Split Lock Mitigation
        self._add_option_row(
            system_group,
            "disable_splitlock",
            _("Disable Split Lock Mitigation"),
            _("Linux has split lock protection that can cause microsecond delays. Disabling removes this 'brake'."),
            "1",
            "0"
        )
        

    
    def _get_cpu_description(self) -> str:
        """Get CPU description based on detected hardware."""
        cpu_type = self.hardware_info.get("cpu_type", "standard")
        if cpu_type == "intel_hybrid":
            return _("Intel Hybrid CPU detected (12th+ gen). Core pinning and parking available.")
        elif cpu_type == "amd_x3d":
            if self.hardware_info.get("supports_amd_x3d_mode", False):
                return _("AMD X3D Dual CCD detected. V-Cache and X3D mode optimizations available.")
            return _("AMD X3D CPU detected. Core pinning available for V-Cache optimization.")
        else:
            return _("Standard CPU detected. Basic scheduling optimizations available.")
    
    def _get_gpu_description(self) -> str:
        """Get GPU description based on detected hardware."""
        parts = []
        if self.hardware_info.get("has_nvidia", False):
            parts.append("NVIDIA")
        if self.hardware_info.get("has_amd", False):
            parts.append("AMD")
        if self.hardware_info.get("has_intel_igpu", False):
            parts.append("Intel iGPU")
            
        server_map = {"wayland": "Wayland", "x11": "X11", "unknown": "Unknown"}
        server = server_map.get(self.hardware_info.get("display_server", "unknown"), "Unknown")
        
        info_str = "Detected: " + ", ".join(parts) if parts else "No dedicated GPU detected"
        info_str += f" ({server})"
        
        return _("{} ⚠️ Overclocking at your own risk!").format(info_str)
    
    def _add_option_row(self, group, key: str, title: str, subtitle: str, value_on: str, value_off: str):
        """Add an option row with a switch."""
        row = Adw.ActionRow(title=title, subtitle=subtitle)
        
        switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        
        # Check current state
        current_value = self.current_config.get(key, "")
        is_active = current_value == value_on
        switch.set_active(is_active)
        
        # Store switch info
        self.option_switches[key] = {
            "switch": switch,
            "value_on": value_on,
            "value_off": value_off
        }
        
        # Connect signal
        switch.connect("state-set", self._on_switch_changed, key, value_on, value_off)
        
        row.add_suffix(switch)
        row.set_activatable_widget(switch)
        group.add(row)
    
    def _on_switch_changed(self, switch, state, key, value_on, value_off):
        """Handle switch toggle - write to config asynchronously."""
        import threading
        
        def run_command():
            if state:
                # Enable option
                subprocess.run([self.script_path, "write", key, value_on], 
                              capture_output=True, timeout=5)
            else:
                # Either remove or set to off value
                if value_off == "" or value_off == "0" or value_off == "no":
                    subprocess.run([self.script_path, "remove", key], 
                                  capture_output=True, timeout=5)
                else:
                    subprocess.run([self.script_path, "write", key, value_off], 
                                  capture_output=True, timeout=5)
        
        # Run in background thread to avoid blocking UI
        thread = threading.Thread(target=run_command, daemon=True)
        thread.start()
        
        return False  # Allow the switch to toggle
    
    def _show_status(self, icon, title, desc):
        """Show status page for errors."""
        status = Adw.StatusPage(icon_name=icon, title=title, description=desc)
        self.inner_box.append(status)

    def _on_restore_defaults(self, button):
        """Ask for confirmation before restoring defaults."""
        dlg = Adw.MessageDialog.new(
            self,
            _("Restore Defaults?"),
            _("This will reset all GameMode configurations to their default values. Custom scripts and optimizations will be overwritten.")
        )
        dlg.add_response("cancel", _("Cancel"))
        dlg.add_response("restore", _("Restore"))
        dlg.set_response_appearance("restore", Adw.ResponseAppearance.DESTRUCTIVE)
        dlg.set_default_response("cancel")
        dlg.connect("response", self._confirm_restore)
        dlg.present()

    def _confirm_restore(self, dialog, response):
        """Execute restore action."""
        if response == "restore":
             # Run script create to overwrite config with defaults
             subprocess.run([self.script_path, "create"], capture_output=True)
             # Reload UI
             self._load_data()


class SteamGamesDialog(Adw.Window):
    """Dialog for configuring Steam games via shell script."""
    
    def __init__(self, parent_window, **kwargs):
        super().__init__(**kwargs)
        self.set_title(_("Configure Steam"))
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

        # Selection Buttons below games list
        selection_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, halign=Gtk.Align.CENTER)
        self.inner_box.append(selection_box)

        for label, callback in [(_("Select All"), lambda b: [c.set_active(True) for c in self.game_checkboxes.values()]),
                                (_("Deselect All"), lambda b: [c.set_active(False) for c in self.game_checkboxes.values()])]:
            btn = Gtk.Button(label=label)
            btn.connect("clicked", callback)
            selection_box.append(btn)
        
        # Footer buttons (Apply and Close) - Centered
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

        # Configure GameMode Option
        gamemode_config_row = Adw.ActionRow()
        gamemode_config_row.set_title(_("Configure GameMode"))
        gamemode_config_row.set_subtitle(_("Advanced CPU/GPU optimizations for gamemode.ini"))
        
        # Settings icon for GameMode config
        gamemode_config_icon_path = os.path.join(ICONS_DIR, "preferences-system-symbolic.svg")
        if os.path.exists(gamemode_config_icon_path):
            gamemode_gfile = Gio.File.new_for_path(gamemode_config_icon_path)
            gamemode_icon = Gio.FileIcon.new(gamemode_gfile)
            gamemode_img = Gtk.Image.new_from_gicon(gamemode_icon)
        else:
            gamemode_img = Gtk.Image.new_from_icon_name("preferences-system-symbolic")
        gamemode_img.set_pixel_size(20)
        gamemode_img.add_css_class("symbolic-icon")
        gamemode_config_row.add_prefix(gamemode_img)
        
        gamemode_open_btn = Gtk.Button(label=_("Open"), valign=Gtk.Align.CENTER)
        gamemode_open_btn.connect("clicked", lambda b: GameModeConfigDialog(self.main_window).present())
        
        gamemode_config_row.add_suffix(gamemode_open_btn)
        row.add_row(gamemode_config_row)     

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
