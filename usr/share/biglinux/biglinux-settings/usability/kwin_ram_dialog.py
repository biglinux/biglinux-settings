#!/usr/bin/env python3
"""
KWin & RAM Master Controller Dialog
A modern GTK4/Adwaita interface for managing KDE visual effects and RAM services.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gio
import subprocess
import threading
import os
import gettext

DOMAIN = 'biglinux-settings'
_ = gettext.gettext


class KWinRamDialog(Adw.Window):
    """Main dialog for KWin & RAM Controller with individual switches."""
    
    def __init__(self, parent_window, script_path, on_close_callback=None):
        super().__init__(modal=True, transient_for=parent_window)
        self.set_default_size(550, 650)
        self.set_title(_("KWin & RAM Controller"))
        
        self.script_path = script_path
        self.on_close_callback = on_close_callback
        self.is_master_active = False
        self.initial_states = {}
        self.updating_switches = False
        
        self._build_ui()
        self._load_initial_states()
    
    def _build_ui(self):
        """Build the modern Adwaita UI."""
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_content(main_box)
        
        # Header Bar
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(True)
        main_box.append(header)
        
        # Scrolled Window
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        main_box.append(scroll)
        
        # Content Box inside scroll
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        content_box.set_margin_start(12)
        content_box.set_margin_end(12)
        content_box.set_margin_top(12)
        content_box.set_margin_bottom(12)
        scroll.set_child(content_box)
        
        # === MASTER CONTROL ===
        master_group = Adw.PreferencesGroup()
        master_group.set_title(_("Master Control"))
        master_group.set_description(_("Enable Performance Mode to apply all optimizations at once"))
        content_box.append(master_group)
        
        # Master Switch Row with Status Page Style
        self.master_row = Adw.ActionRow()
        self.master_row.set_title(_("Performance Mode"))
        self.master_row.set_subtitle(_("Disable all effects and optimize RAM"))
        
        # Icon
        master_icon = Gtk.Image.new_from_icon_name("input-gaming-symbolic")
        master_icon.set_pixel_size(32)
        master_icon.add_css_class("accent")
        self.master_row.add_prefix(master_icon)
        
        # Master Switch
        self.master_switch = Gtk.Switch()
        self.master_switch.set_valign(Gtk.Align.CENTER)
        self.master_switch.connect("state-set", self._on_master_toggled)
        self.master_row.add_suffix(self.master_switch)
        self.master_row.set_activatable_widget(self.master_switch)
        
        master_group.add(self.master_row)
        
        # === GPU & EFFECTS ===
        gpu_group = Adw.PreferencesGroup()
        gpu_group.set_title(_("GPU & Visual Effects"))
        gpu_group.set_description(_("Control KWin compositor effects"))
        content_box.append(gpu_group)
        
        # Effects Switch
        self.effects_row = Adw.ActionRow()
        self.effects_row.set_title(_("Visual Effects"))
        self.effects_row.set_subtitle(_("Blur, Wobbly Windows, Shadows, Animations"))
        self.effects_row.add_prefix(Gtk.Image.new_from_icon_name("preferences-desktop-effects-symbolic"))
        
        self.effects_switch = Gtk.Switch()
        self.effects_switch.set_valign(Gtk.Align.CENTER)
        self.effects_switch.connect("state-set", self._on_effects_toggled)
        self.effects_row.add_suffix(self.effects_switch)
        self.effects_row.set_activatable_widget(self.effects_switch)
        gpu_group.add(self.effects_row)
        
        # Compositor Settings
        self.compositor_row = Adw.ActionRow()
        self.compositor_row.set_title(_("Compositor Settings"))
        self.compositor_row.set_subtitle(_("Animations, Latency Policy, Tearing"))
        self.compositor_row.add_prefix(Gtk.Image.new_from_icon_name("preferences-desktop-display-symbolic"))
        
        self.compositor_switch = Gtk.Switch()
        self.compositor_switch.set_valign(Gtk.Align.CENTER)
        self.compositor_switch.connect("state-set", self._on_compositor_toggled)
        self.compositor_row.add_suffix(self.compositor_switch)
        self.compositor_row.set_activatable_widget(self.compositor_switch)
        gpu_group.add(self.compositor_row)
        
        # === RAM & SERVICES ===
        ram_group = Adw.PreferencesGroup()
        ram_group.set_title(_("Memory & Services"))
        ram_group.set_description(_("Control background services that consume RAM"))
        content_box.append(ram_group)
        
        # Baloo Indexer
        self.baloo_row = Adw.ActionRow()
        self.baloo_row.set_title(_("Baloo File Indexer"))
        self.baloo_row.set_subtitle(_("File search indexing service"))
        self.baloo_row.add_prefix(Gtk.Image.new_from_icon_name("system-search-symbolic"))
        
        self.baloo_switch = Gtk.Switch()
        self.baloo_switch.set_valign(Gtk.Align.CENTER)
        self.baloo_switch.connect("state-set", self._on_baloo_toggled)
        self.baloo_row.add_suffix(self.baloo_switch)
        self.baloo_row.set_activatable_widget(self.baloo_switch)
        ram_group.add(self.baloo_row)
        
        # Akonadi Server
        self.akonadi_row = Adw.ActionRow()
        self.akonadi_row.set_title(_("Akonadi Server"))
        self.akonadi_row.set_subtitle(_("PIM storage service (Contacts, Calendar)"))
        self.akonadi_row.add_prefix(Gtk.Image.new_from_icon_name("x-office-address-book-symbolic"))
        
        self.akonadi_switch = Gtk.Switch()
        self.akonadi_switch.set_valign(Gtk.Align.CENTER)
        self.akonadi_switch.connect("state-set", self._on_akonadi_toggled)
        self.akonadi_row.add_suffix(self.akonadi_switch)
        self.akonadi_row.set_activatable_widget(self.akonadi_switch)
        ram_group.add(self.akonadi_row)
        
        # SMART Monitor
        self.smart_row = Adw.ActionRow()
        self.smart_row.set_title(_("S.M.A.R.T Monitor"))
        self.smart_row.set_subtitle(_("Disk health monitoring daemon"))
        self.smart_row.add_prefix(Gtk.Image.new_from_icon_name("drive-harddisk-symbolic"))
        
        self.smart_switch = Gtk.Switch()
        self.smart_switch.set_valign(Gtk.Align.CENTER)
        self.smart_switch.connect("state-set", self._on_smart_toggled)
        self.smart_row.add_suffix(self.smart_switch)
        self.smart_row.set_activatable_widget(self.smart_switch)
        ram_group.add(self.smart_row)
        
        # === CACHE ACTIONS ===
        cache_group = Adw.PreferencesGroup()
        cache_group.set_title(_("Cache Management"))
        cache_group.set_description(_("Clear system memory caches"))
        content_box.append(cache_group)
        
        # Cache Clean Button
        cache_row = Adw.ActionRow()
        cache_row.set_title(_("Clear RAM Cache"))
        cache_row.set_subtitle(_("Free memory marked as Buff/Cache (requires sudo)"))
        cache_row.add_prefix(Gtk.Image.new_from_icon_name("user-trash-symbolic"))
        
        self.cache_button = Gtk.Button(label=_("Clean Now"))
        self.cache_button.add_css_class("suggested-action")
        self.cache_button.set_valign(Gtk.Align.CENTER)
        self.cache_button.connect("clicked", self._on_clean_cache)
        cache_row.add_suffix(self.cache_button)
        cache_group.add(cache_row)
        
        # === STATUS BAR ===
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        status_box.set_margin_start(12)
        status_box.set_margin_end(12)
        status_box.set_margin_top(12)
        status_box.set_margin_bottom(12)
        status_box.set_halign(Gtk.Align.CENTER)
        
        self.status_spinner = Gtk.Spinner()
        status_box.append(self.status_spinner)
        
        self.status_label = Gtk.Label(label=_("Ready"))
        self.status_label.add_css_class("dim-label")
        status_box.append(self.status_label)
        
        main_box.append(status_box)
        
        # === ACTION BUTTONS ===
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12, halign=Gtk.Align.CENTER)
        button_box.set_margin_bottom(20)
        
        close_btn = Gtk.Button(label=_("Close"))
        close_btn.add_css_class("pill")
        close_btn.connect("clicked", lambda b: self.close())
        button_box.append(close_btn)
        
        main_box.append(button_box)
    
    def _load_initial_states(self):
        """Load current states of all services."""
        self.updating_switches = True
        self._set_status(_("Loading..."), True)
        
        def load_thread():
            states = {}
            
            # Effects
            result = self._run_script_sync("get_effects_status")
            states['effects'] = result.strip() == "true"
            
            # Baloo
            result = self._run_script_sync("get_baloo_status")
            if result.strip() == "NOT_INSTALLED":
                states['baloo'] = None
            else:
                states['baloo'] = result.strip() == "true"
            
            # Akonadi
            result = self._run_script_sync("get_akonadi_status")
            if result.strip() == "NOT_INSTALLED":
                states['akonadi'] = None
            else:
                states['akonadi'] = result.strip() == "true"
            
            # Compositor
            result = self._run_script_sync("get_compositor_status")
            states['compositor'] = result.strip() == "true"
            
            # Master check (inverse of performance mode)
            result = self._run_script_sync("check")
            states['master'] = result.strip() == "true"  # Performance mode active
            
            GLib.idle_add(self._apply_loaded_states, states)
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def _apply_loaded_states(self, states):
        """Apply loaded states to switches."""
        self.initial_states = states
        
        # Effects and Compositor are "on" when desktop mode (not performance)
        self.effects_switch.set_active(states.get('effects', True))
        self.compositor_switch.set_active(states.get('compositor', True))
        
        # Baloo
        if states.get('baloo') is None:
            self.baloo_switch.set_sensitive(False)
            self.baloo_row.set_subtitle(_("Not installed"))
        else:
            self.baloo_switch.set_active(states.get('baloo', True))
        
        # Akonadi
        if states.get('akonadi') is None:
            self.akonadi_switch.set_sensitive(False)
            self.akonadi_row.set_subtitle(_("Not installed"))
        else:
            self.akonadi_switch.set_active(states.get('akonadi', True))
        
        # SMART - always assume available
        self.smart_switch.set_active(True)  # Default on
        
        # Master switch
        self.master_switch.set_active(states.get('master', False))
        self.is_master_active = states.get('master', False)
        
        self._update_individual_switches_state()
        
        self.updating_switches = False
        self._set_status(_("Ready"), False)
    
    def _run_script_sync(self, *args):
        """Run script synchronously and return output."""
        try:
            cmd = ["pkexec", self.script_path] + list(args)
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.stdout
        except Exception as e:
            return ""
    
    def _run_script_async(self, *args, callback=None):
        """Run script asynchronously."""
        def run():
            try:
                cmd = ["pkexec", self.script_path] + list(args)
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                if callback:
                    GLib.idle_add(callback, result.returncode == 0)
            except Exception as e:
                if callback:
                    GLib.idle_add(callback, False)
        
        threading.Thread(target=run, daemon=True).start()
    
    def _set_status(self, text, spinning=False):
        """Update status bar."""
        self.status_label.set_text(text)
        if spinning:
            self.status_spinner.start()
            self.status_spinner.set_visible(True)
        else:
            self.status_spinner.stop()
            self.status_spinner.set_visible(False)
    
    def _update_individual_switches_state(self):
        """Enable/disable individual switches based on master state."""
        # When master is ON (performance mode), disable individual controls
        sensitive = not self.is_master_active
        
        self.effects_switch.set_sensitive(sensitive)
        self.compositor_switch.set_sensitive(sensitive)
        
        # Only if installed
        if self.initial_states.get('baloo') is not None:
            self.baloo_switch.set_sensitive(sensitive)
        if self.initial_states.get('akonadi') is not None:
            self.akonadi_switch.set_sensitive(sensitive)
        
        self.smart_switch.set_sensitive(sensitive)
    
    # === EVENT HANDLERS ===
    
    def _on_master_toggled(self, switch, state):
        """Handle master switch toggle."""
        if self.updating_switches:
            return False
        
        self.is_master_active = state
        self._update_individual_switches_state()
        
        if state:
            # Enable performance mode
            self._set_status(_("Enabling Performance Mode..."), True)
            
            def on_done(success):
                if success:
                    self._set_status(_("Performance Mode Active"), False)
                    # Update switches to reflect disabled state
                    self.updating_switches = True
                    self.effects_switch.set_active(False)
                    self.compositor_switch.set_active(False)
                    if self.initial_states.get('baloo') is not None:
                        self.baloo_switch.set_active(False)
                    if self.initial_states.get('akonadi') is not None:
                        self.akonadi_switch.set_active(False)
                    self.smart_switch.set_active(False)
                    self.updating_switches = False
                else:
                    self._set_status(_("Failed"), False)
                    switch.set_active(False)
            
            self._run_script_async("enable_gui", callback=on_done)
        else:
            # Restore desktop mode
            self._set_status(_("Restoring Desktop Mode..."), True)
            
            def on_done(success):
                if success:
                    self._set_status(_("Desktop Mode Restored"), False)
                    # Restore original states
                    self.updating_switches = True
                    self.effects_switch.set_active(True)
                    self.compositor_switch.set_active(True)
                    if self.initial_states.get('baloo') is not None:
                        self.baloo_switch.set_active(self.initial_states.get('baloo', True))
                    if self.initial_states.get('akonadi') is not None:
                        self.akonadi_switch.set_active(self.initial_states.get('akonadi', True))
                    self.smart_switch.set_active(True)
                    self.updating_switches = False
                else:
                    self._set_status(_("Failed"), False)
                    switch.set_active(True)
            
            self._run_script_async("disable_gui", callback=on_done)
        
        return False
    
    def _on_effects_toggled(self, switch, state):
        """Handle effects switch toggle."""
        if self.updating_switches:
            return False
        
        self._set_status(_("Toggling Effects..."), True)
        state_str = "true" if state else "false"
        
        def on_done(success):
            if success:
                self._set_status(_("Effects {}").format(_("enabled") if state else _("disabled")), False)
            else:
                self._set_status(_("Failed"), False)
                switch.set_active(not state)
        
        self._run_script_async("toggle_effects", state_str, callback=on_done)
        return False
    
    def _on_compositor_toggled(self, switch, state):
        """Handle compositor settings toggle."""
        if self.updating_switches:
            return False
        
        self._set_status(_("Updating Compositor..."), True)
        state_str = "true" if state else "false"
        
        def on_done(success):
            if success:
                self._set_status(_("Compositor settings updated"), False)
            else:
                self._set_status(_("Failed"), False)
                switch.set_active(not state)
        
        self._run_script_async("toggle_compositor", state_str, callback=on_done)
        return False
    
    def _on_baloo_toggled(self, switch, state):
        """Handle Baloo toggle."""
        if self.updating_switches:
            return False
        
        self._set_status(_("Toggling Baloo..."), True)
        state_str = "true" if state else "false"
        
        def on_done(success):
            if success:
                self._set_status(_("Baloo {}").format(_("resumed") if state else _("suspended")), False)
            else:
                self._set_status(_("Failed"), False)
                switch.set_active(not state)
        
        self._run_script_async("toggle_baloo", state_str, callback=on_done)
        return False
    
    def _on_akonadi_toggled(self, switch, state):
        """Handle Akonadi toggle."""
        if self.updating_switches:
            return False
        
        self._set_status(_("Toggling Akonadi..."), True)
        state_str = "true" if state else "false"
        
        def on_done(success):
            if success:
                self._set_status(_("Akonadi {}").format(_("started") if state else _("stopped")), False)
            else:
                self._set_status(_("Failed"), False)
                switch.set_active(not state)
        
        self._run_script_async("toggle_akonadi", state_str, callback=on_done)
        return False
    
    def _on_smart_toggled(self, switch, state):
        """Handle SMART toggle."""
        if self.updating_switches:
            return False
        
        self._set_status(_("Toggling SMART Monitor..."), True)
        state_str = "true" if state else "false"
        
        def on_done(success):
            if success:
                self._set_status(_("SMART {}").format(_("loaded") if state else _("unloaded")), False)
            else:
                self._set_status(_("Failed"), False)
                switch.set_active(not state)
        
        self._run_script_async("toggle_smart", state_str, callback=on_done)
        return False
    
    def _on_clean_cache(self, button):
        """Handle cache clean button."""
        self._set_status(_("Cleaning Cache..."), True)
        self.cache_button.set_sensitive(False)
        
        def on_done(success):
            self.cache_button.set_sensitive(True)
            if success:
                self._set_status(_("Cache cleaned successfully!"), False)
            else:
                self._set_status(_("Failed to clean cache"), False)
        
        self._run_script_async("clean_cache", callback=on_done)


# For standalone testing
if __name__ == "__main__":
    app = Adw.Application(application_id="com.biglinux.kwinram.test")
    
    def on_activate(app):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, "kwin_ram_controller.sh")
        
        win = KWinRamDialog(None, script_path)
        win.set_application(app)
        win.present()
    
    app.connect("activate", on_activate)
    app.run(None)
