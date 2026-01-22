
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib
import gettext
import os

DOMAIN = 'biglinux-settings'
_ = gettext.gettext

class GameModeConfigDialog(Adw.Window):
    """Configuration dialog for Game Mode Booster with individual switches."""
    
    def __init__(self, parent_window, on_confirm_callback=None, on_cancel_callback=None):
        super().__init__(modal=True, transient_for=parent_window)
        self.set_default_size(550, 600)
        self.set_title(_("Game Mode Booster Configuration"))
        
        self.on_confirm_callback = on_confirm_callback
        self.on_cancel_callback = on_cancel_callback
        
        # Store configuration
        self.config = {
            'gamemode': True,
            'visual_effects': True,
            'compositor': True,
            'baloo': True,
            'akonadi': True,
            'smart': True,
            'gpu': True
        }
        
        self.is_confirmed = False
        self.connect("close-request", self._on_close_request)
        self._build_ui()
    
    def _on_close_request(self, window):
        """Handle window close request (X button)."""
        if not self.is_confirmed and self.on_cancel_callback:
            self.on_cancel_callback()
        return False

    def _build_ui(self):
        """Build the configuration UI."""
        # Main Box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_content(main_box)
        
        # Header Bar with Icon
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(True)
        
        # Add icon to header
        header_icon = Gtk.Image.new_from_icon_name("input-gaming-symbolic")
        header_icon.set_pixel_size(24)
        header.pack_start(header_icon)
        
        main_box.append(header)
        
        # Scrolled Window
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        main_box.append(scroll)
        
        # Content Box
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        content_box.set_margin_start(12)
        content_box.set_margin_end(12)
        content_box.set_margin_top(12)
        content_box.set_margin_bottom(12)
        scroll.set_child(content_box)
        
        # === OPTIMIZATIONS ===
        opt_group = Adw.PreferencesGroup()
        opt_group.set_title(_("Optimizations"))
        content_box.append(opt_group)
        
        # GameMode Daemon
        self.gamemode_row = self._create_switch_row(
            _("GameMode Daemon"),
            _("System-wide performance daemon"),
            "input-gaming-symbolic",
            "gamemode"
        )
        opt_group.add(self.gamemode_row)
        
        # Visual Effects
        self.effects_row = self._create_switch_row(
            _("Disable Visual Effects"),
            _("Turn off KWin effects (blur, shadows, animations)"),
            "preferences-desktop-effects-symbolic",
            "visual_effects"
        )
        opt_group.add(self.effects_row)
        
        # Compositor Settings
        self.compositor_row = self._create_switch_row(
            _("Compositor Settings"),
            _("Low latency, allow tearing, no animations"),
            "preferences-desktop-display-symbolic",
            "compositor"
        )
        opt_group.add(self.compositor_row)
        
        # GPU Performance
        self.gpu_row = self._create_switch_row(
            _("GPU Maximum Performance"),
            _("Force maximum performance mode (NVIDIA/AMD)"),
            "application-x-addon-symbolic",
            "gpu"
        )
        opt_group.add(self.gpu_row)
        
        # Baloo
        self.baloo_row = self._create_switch_row(
            _("Suspend Baloo Indexer"),
            _("Stop file indexing service"),
            "system-search-symbolic",
            "baloo"
        )
        opt_group.add(self.baloo_row)
        
        # Akonadi
        self.akonadi_row = self._create_switch_row(
            _("Stop Akonadi Server"),
            _("Stop PIM storage service"),
            "x-office-address-book-symbolic",
            "akonadi"
        )
        opt_group.add(self.akonadi_row)
        
        # SMART
        self.smart_row = self._create_switch_row(
            _("Unload S.M.A.R.T Monitor"),
            _("Stop disk health monitoring"),
            "drive-harddisk-symbolic",
            "smart"
        )
        opt_group.add(self.smart_row)
        
        # === NETWORK OPTIMIZATIONS ===

        
        # === ACTION BUTTONS ===
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12, halign=Gtk.Align.CENTER)
        button_box.set_margin_top(20)
        button_box.set_margin_bottom(20)
        
        # Cancel Button
        cancel_btn = Gtk.Button(label=_("Cancel"))
        cancel_btn.add_css_class("pill")
        cancel_btn.connect("clicked", self._on_cancel)
        button_box.append(cancel_btn)
        
        # Apply Button
        apply_btn = Gtk.Button(label=_("Apply Optimizations"))
        apply_btn.add_css_class("pill")
        apply_btn.add_css_class("suggested-action")
        apply_btn.connect("clicked", self._on_apply)
        button_box.append(apply_btn)
        
        main_box.append(button_box)
    
    def _create_switch_row(self, title, subtitle, icon, config_key):
        """Create a switch row for configuration."""
        row = Adw.ActionRow()
        row.set_title(title)
        row.set_subtitle(subtitle)
        row.add_prefix(Gtk.Image.new_from_icon_name(icon))
        
        switch = Gtk.Switch()
        switch.set_active(self.config[config_key])
        switch.set_valign(Gtk.Align.CENTER)
        switch.connect("state-set", self._on_switch_changed, config_key)
        
        row.add_suffix(switch)
        row.set_activatable_widget(switch)
        
        return row
    
    def _on_switch_changed(self, switch, state, config_key):
        """Handle switch state changes."""
        self.config[config_key] = state
        return False
    
    def _on_cancel(self, button):
        """Handle cancel button."""
        # Callback handled by close-request or we can call it here explicitly
        # If we call close(), close-request will fire.
        # Since is_confirmed is False, close-request will call the callback.
        # So we just close.
        self.close()
    
    def _on_apply(self, button):
        """Handle apply button."""
        self.is_confirmed = True
        if self.on_confirm_callback:
            self.on_confirm_callback(self.config)
        self.close()
    
    def get_config(self):
        """Get current configuration."""
        return self.config


# For standalone testing
if __name__ == "__main__":
    app = Adw.Application(application_id="com.biglinux.gamemode.config.test")
    
    def on_activate(app):
        def on_confirm(config):
            print("Config:", config)
        
        def on_cancel():
            print("Cancelled")
        
        win = GameModeConfigDialog(None, on_confirm, on_cancel)
        win.set_application(app)
        win.present()
    
    app.connect("activate", on_activate)
    app.run(None)
