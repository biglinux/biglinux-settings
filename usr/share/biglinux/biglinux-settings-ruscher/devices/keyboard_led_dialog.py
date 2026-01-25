#!/usr/bin/env python3
"""
LED Master - Advanced Keyboard LED Configuration Dialog
GTK4/Adwaita dialog for configuring keyboard LED device with full features
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib, Gdk
import subprocess
import os
import gettext

DOMAIN = 'biglinux-settings'
LOCALE_DIR = '/usr/share/locale'
gettext.bindtextdomain(DOMAIN, LOCALE_DIR)
gettext.textdomain(DOMAIN)
_ = gettext.gettext


class KeyboardLEDDialog(Adw.Dialog):
    """Advanced dialog for configuring keyboard LED device"""
    
    def __init__(self, parent_window, script_path, on_complete_callback=None):
        super().__init__()
        self.parent_window = parent_window
        self.script_path = script_path
        self.on_complete_callback = on_complete_callback
        self.devices = []
        self.current_device_index = 0
        self.selected_device = None
        self.session_type = self._get_session_type()
        self.capturing_hotkey = False
        self.configuration_completed = False  # Track if config was finished
        
        self.set_title(_("LED Master"))
        self.set_content_width(500)
        self.set_content_height(500)
        
        # Connect to closed signal to handle cancel/close
        self.connect("closed", self.on_dialog_closed)
        
        self.setup_ui()
        
    def _get_session_type(self):
        """Get current session type (x11 or wayland)"""
        try:
            result = subprocess.run(
                [self.script_path, "get_session"],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip()
        except:
            return os.environ.get("XDG_SESSION_TYPE", "x11")
        
    def setup_ui(self):
        """Build the dialog UI"""
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_child(main_box)
        
        # Header Bar
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(True)
        header.set_show_start_title_buttons(False)
        main_box.append(header)
        
        # Cancel button
        cancel_btn = Gtk.Button(label=_("Cancel"))
        cancel_btn.connect("clicked", lambda b: self.close())
        header.pack_start(cancel_btn)
        
        # Content with proper scrolling
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        main_box.append(scrolled)
        
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_top(24)
        content.set_margin_bottom(24)
        content.set_margin_start(24)
        content.set_margin_end(24)
        scrolled.set_child(content)
        
        # Stack for different views
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_vexpand(True)
        content.append(self.stack)
        
        # Create all pages
        self.create_welcome_page()
        self.create_testing_page()
        self.create_options_page()
        self.create_hotkey_page()
        self.create_success_page()
        self.create_no_devices_page()
        
    def create_welcome_page(self):
        """Create the welcome/introduction page"""
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        page.set_valign(Gtk.Align.CENTER)
        
        # Icon with animated style
        icon_box = Gtk.Box()
        icon_box.set_halign(Gtk.Align.CENTER)
        icon = Gtk.Image.new_from_icon_name("keyboard-brightness-symbolic")
        icon.set_pixel_size(80)
        icon.add_css_class("accent")
        icon_box.append(icon)
        page.append(icon_box)
        
        # Title
        title = Gtk.Label(label=_("LED Master"))
        title.add_css_class("title-1")
        page.append(title)
        
        # Subtitle
        subtitle = Gtk.Label(label=_("Advanced Keyboard LED Control"))
        subtitle.add_css_class("title-4")
        subtitle.add_css_class("dim-label")
        page.append(subtitle)
        
        # Description
        desc = Gtk.Label(
            label=_("This wizard will help you configure your keyboard LED.\n\n"
                   "We will:\n"
                   "• Detect available LED devices\n"
                   "• Test each device to find your keyboard LED\n"
                   "• Configure options like hotkeys and autostart")
        )
        desc.set_wrap(True)
        desc.set_justify(Gtk.Justification.CENTER)
        desc.add_css_class("body")
        desc.set_margin_top(16)
        page.append(desc)
        
        # Session type info
        session_label = Gtk.Label(label=_("Session: {}").format(self.session_type.upper()))
        session_label.add_css_class("caption")
        session_label.add_css_class("dim-label")
        session_label.set_margin_top(8)
        page.append(session_label)
        
        # Start button
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.CENTER)
        btn_box.set_margin_top(24)
        page.append(btn_box)
        
        start_btn = Gtk.Button(label=_("Start Configuration"))
        start_btn.add_css_class("suggested-action")
        start_btn.add_css_class("pill")
        start_btn.connect("clicked", self.on_start_clicked)
        btn_box.append(start_btn)
        
        self.stack.add_named(page, "welcome")
        
    def create_testing_page(self):
        """Create the device testing page"""
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        page.set_valign(Gtk.Align.CENTER)
        
        # Animated icon
        icon = Gtk.Image.new_from_icon_name("dialog-question-symbolic")
        icon.set_pixel_size(64)
        icon.add_css_class("warning")
        page.append(icon)
        
        # Title
        title = Gtk.Label(label=_("Did the LED turn on?"))
        title.add_css_class("title-2")
        page.append(title)
        
        # Device info card
        info_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        info_card.add_css_class("card")
        info_card.set_margin_top(8)
        info_card.set_margin_bottom(8)
        info_card.set_margin_start(32)
        info_card.set_margin_end(32)
        page.append(info_card)
        
        # Device name label
        self.device_label = Gtk.Label(label="")
        self.device_label.add_css_class("caption")
        self.device_label.add_css_class("monospace")
        self.device_label.set_margin_top(12)
        self.device_label.set_margin_bottom(6)
        self.device_label.set_margin_start(12)
        self.device_label.set_margin_end(12)
        self.device_label.set_selectable(True)
        info_card.append(self.device_label)
        
        # Method label
        self.method_label = Gtk.Label(label="")
        self.method_label.add_css_class("caption")
        self.method_label.add_css_class("dim-label")
        self.method_label.set_margin_bottom(12)
        info_card.append(self.method_label)
        
        # Progress indicator
        self.progress_label = Gtk.Label(label="")
        self.progress_label.add_css_class("caption")
        self.progress_label.set_margin_top(8)
        page.append(self.progress_label)
        
        # Progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_margin_start(48)
        self.progress_bar.set_margin_end(48)
        page.append(self.progress_bar)
        
        # Buttons
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.CENTER)
        btn_box.set_margin_top(24)
        page.append(btn_box)
        
        no_btn = Gtk.Button(label=_("No, try next"))
        no_btn.add_css_class("destructive-action")
        no_btn.add_css_class("pill")
        no_btn.connect("clicked", self.on_no_clicked)
        btn_box.append(no_btn)
        
        yes_btn = Gtk.Button(label=_("Yes, this is my LED!"))
        yes_btn.add_css_class("suggested-action")
        yes_btn.add_css_class("pill")
        yes_btn.connect("clicked", self.on_yes_clicked)
        btn_box.append(yes_btn)
        
        self.stack.add_named(page, "testing")
        
    def create_options_page(self):
        """Create the advanced options page"""
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        # Title
        title = Gtk.Label(label=_("Additional Options"))
        title.add_css_class("title-2")
        title.set_margin_bottom(12)
        page.append(title)
        
        # Preferences group
        group = Adw.PreferencesGroup()
        group.set_title(_("Settings"))
        page.append(group)
        
        # Xmodmap option (X11 only)
        self.xmodmap_row = Adw.SwitchRow()
        self.xmodmap_row.set_title(_("Apply Scroll Lock Fix"))
        self.xmodmap_row.set_subtitle(_("Fix for keyboards where Scroll Lock doesn't work properly (xmodmap)"))
        self.xmodmap_row.set_icon_name("preferences-system-keyboard-symbolic")
        
        if self.session_type != "x11":
            self.xmodmap_row.set_sensitive(False)
            self.xmodmap_row.set_subtitle(_("Only available on X11 sessions"))
        
        group.add(self.xmodmap_row)
        
        # Autostart option
        self.autostart_row = Adw.SwitchRow()
        self.autostart_row.set_title(_("Start with System"))
        self.autostart_row.set_subtitle(_("Turn on LED automatically when you log in"))
        self.autostart_row.set_icon_name("system-run-symbolic")
        self.autostart_row.set_active(True)  # Default to enabled
        group.add(self.autostart_row)
        
        # Hotkey option
        hotkey_group = Adw.PreferencesGroup()
        hotkey_group.set_title(_("Keyboard Shortcut"))
        hotkey_group.set_margin_top(16)
        page.append(hotkey_group)
        
        self.hotkey_row = Adw.ActionRow()
        self.hotkey_row.set_title(_("Toggle LED Hotkey"))
        self.hotkey_row.set_subtitle(_("Press a key to toggle the LED on/off"))
        self.hotkey_row.set_icon_name("preferences-desktop-keyboard-shortcuts-symbolic")
        
        if self.session_type != "x11":
            self.hotkey_row.set_sensitive(False)
            self.hotkey_row.set_subtitle(_("Only available on X11 sessions"))
        
        # Hotkey display label
        self.hotkey_label = Gtk.Label(label=_("Not set"))
        self.hotkey_label.add_css_class("dim-label")
        self.hotkey_row.add_suffix(self.hotkey_label)
        
        # Set hotkey button
        set_hotkey_btn = Gtk.Button()
        set_hotkey_btn.set_icon_name("input-keyboard-symbolic")
        set_hotkey_btn.add_css_class("flat")
        set_hotkey_btn.set_valign(Gtk.Align.CENTER)
        set_hotkey_btn.set_tooltip_text(_("Set hotkey"))
        set_hotkey_btn.connect("clicked", self.on_set_hotkey_clicked)
        self.hotkey_row.add_suffix(set_hotkey_btn)
        
        hotkey_group.add(self.hotkey_row)
        
        # Next button
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.CENTER)
        btn_box.set_margin_top(32)
        btn_box.set_valign(Gtk.Align.END)
        btn_box.set_vexpand(True)
        page.append(btn_box)
        
        back_btn = Gtk.Button(label=_("Back"))
        back_btn.add_css_class("pill")
        back_btn.connect("clicked", lambda b: self.stack.set_visible_child_name("testing"))
        btn_box.append(back_btn)
        
        finish_btn = Gtk.Button(label=_("Finish Configuration"))
        finish_btn.add_css_class("suggested-action")
        finish_btn.add_css_class("pill")
        finish_btn.connect("clicked", self.on_finish_clicked)
        btn_box.append(finish_btn)
        
        self.stack.add_named(page, "options")
        
    def create_hotkey_page(self):
        """Create the hotkey capture page"""
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        page.set_valign(Gtk.Align.CENTER)
        
        # Icon
        icon = Gtk.Image.new_from_icon_name("input-keyboard-symbolic")
        icon.set_pixel_size(64)
        icon.add_css_class("accent")
        page.append(icon)
        
        # Title
        title = Gtk.Label(label=_("Press the desired key"))
        title.add_css_class("title-2")
        page.append(title)
        
        # Description
        desc = Gtk.Label(
            label=_("A small window will appear.\n"
                   "Click on it and press the key you want to use\n"
                   "to toggle the LED on/off.")
        )
        desc.set_wrap(True)
        desc.set_justify(Gtk.Justification.CENTER)
        desc.add_css_class("body")
        page.append(desc)
        
        # Spinner for capturing
        self.capture_spinner = Gtk.Spinner()
        self.capture_spinner.set_size_request(48, 48)
        page.append(self.capture_spinner)
        
        # Status label
        self.capture_status = Gtk.Label(label=_("Waiting..."))
        self.capture_status.add_css_class("caption")
        self.capture_status.add_css_class("dim-label")
        page.append(self.capture_status)
        
        # Buttons
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.CENTER)
        btn_box.set_margin_top(24)
        page.append(btn_box)
        
        cancel_btn = Gtk.Button(label=_("Cancel"))
        cancel_btn.add_css_class("pill")
        cancel_btn.connect("clicked", self.on_cancel_hotkey_capture)
        btn_box.append(cancel_btn)
        
        self.stack.add_named(page, "hotkey")
        
    def create_success_page(self):
        """Create the success page"""
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        page.set_valign(Gtk.Align.CENTER)
        
        # Icon
        icon = Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
        icon.set_pixel_size(80)
        icon.add_css_class("success")
        page.append(icon)
        
        # Title
        title = Gtk.Label(label=_("Configuration Complete!"))
        title.add_css_class("title-1")
        page.append(title)
        
        # Summary card
        summary_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        summary_card.add_css_class("card")
        summary_card.set_margin_top(16)
        summary_card.set_margin_start(32)
        summary_card.set_margin_end(32)
        page.append(summary_card)
        
        # Device saved label
        self.saved_device_label = Gtk.Label(label="")
        self.saved_device_label.add_css_class("caption")
        self.saved_device_label.add_css_class("monospace")
        self.saved_device_label.set_margin_top(12)
        self.saved_device_label.set_margin_start(12)
        self.saved_device_label.set_margin_end(12)
        summary_card.append(self.saved_device_label)
        
        # Options summary
        self.options_summary = Gtk.Label(label="")
        self.options_summary.add_css_class("caption")
        self.options_summary.add_css_class("dim-label")
        self.options_summary.set_margin_bottom(12)
        self.options_summary.set_margin_start(12)
        self.options_summary.set_margin_end(12)
        summary_card.append(self.options_summary)
        
        # Description
        desc = Gtk.Label(
            label=_("Your keyboard LED is now configured and ready to use.")
        )
        desc.set_wrap(True)
        desc.set_justify(Gtk.Justification.CENTER)
        desc.add_css_class("body")
        desc.set_margin_top(16)
        page.append(desc)
        
        # Close button
        close_btn = Gtk.Button(label=_("Done"))
        close_btn.add_css_class("suggested-action")
        close_btn.add_css_class("pill")
        close_btn.set_halign(Gtk.Align.CENTER)
        close_btn.set_margin_top(24)
        close_btn.connect("clicked", self.on_done_clicked)
        page.append(close_btn)
        
        self.stack.add_named(page, "success")
        
    def create_no_devices_page(self):
        """Create the no devices found page"""
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        page.set_valign(Gtk.Align.CENTER)
        
        # Icon
        icon = Gtk.Image.new_from_icon_name("dialog-error-symbolic")
        icon.set_pixel_size(80)
        icon.add_css_class("error")
        page.append(icon)
        
        # Title
        title = Gtk.Label(label=_("No Compatible Device Found"))
        title.add_css_class("title-1")
        page.append(title)
        
        # Description with troubleshooting tips
        desc = Gtk.Label(
            label=_("Could not find a compatible keyboard LED device.\n\n"
                   "Troubleshooting tips:\n"
                   "• Make sure your keyboard has LED support\n"
                   "• Install brightnessctl: sudo pacman -S brightnessctl\n"
                   "• On X11, xset is also used to control LEDs\n"
                   "• Try running: brightnessctl -l")
        )
        desc.set_wrap(True)
        desc.set_justify(Gtk.Justification.CENTER)
        desc.add_css_class("body")
        page.append(desc)
        
        # Close button
        close_btn = Gtk.Button(label=_("Close"))
        close_btn.add_css_class("pill")
        close_btn.set_halign(Gtk.Align.CENTER)
        close_btn.set_margin_top(24)
        close_btn.connect("clicked", self.on_close_no_device)
        page.append(close_btn)
        
        self.stack.add_named(page, "no_devices")
        
    def on_start_clicked(self, button):
        """Start the device detection process"""
        # Get list of devices from script
        try:
            result = subprocess.run(
                [self.script_path, "get_candidates"],
                capture_output=True,
                text=True,
                timeout=10
            )
            devices_raw = result.stdout.strip()
            self.devices = [d.strip() for d in devices_raw.split('\n') if d.strip()]
        except Exception as e:
            print(f"Error getting devices: {e}")
            self.devices = []
        
        if not self.devices:
            self.stack.set_visible_child_name("no_devices")
            return
        
        self.current_device_index = 0
        self.test_current_device()
        
    def test_current_device(self):
        """Test the current device in the list"""
        if self.current_device_index >= len(self.devices):
            # No more devices to test
            self.stack.set_visible_child_name("no_devices")
            return
        
        device = self.devices[self.current_device_index]
        
        # Determine method for display
        if device.startswith("xset:"):
            method = "xset"
            device_display = device.replace("xset:", "LED #")
        else:
            method = "brightnessctl"
            device_display = device
        
        # Update labels
        self.device_label.set_label(device_display)
        self.method_label.set_label(_("Method: {}").format(method))
        self.progress_label.set_label(_("Testing {} of {}").format(
            self.current_device_index + 1, 
            len(self.devices)
        ))
        
        # Update progress bar
        progress = (self.current_device_index + 1) / len(self.devices)
        self.progress_bar.set_fraction(progress)
        
        # Turn on this device
        try:
            subprocess.run(
                [self.script_path, "test", device],
                capture_output=True,
                timeout=5
            )
        except Exception as e:
            print(f"Error testing device {device}: {e}")
        
        # Show testing page
        self.stack.set_visible_child_name("testing")
        
    def on_no_clicked(self, button):
        """User said NO - try next device"""
        # Turn off current device
        device = self.devices[self.current_device_index]
        try:
            subprocess.run(
                [self.script_path, "test_off", device],
                capture_output=True,
                timeout=5
            )
        except:
            pass
        
        # Try next device
        self.current_device_index += 1
        self.test_current_device()
        
    def on_yes_clicked(self, button):
        """User said YES - save this device and show options"""
        device = self.devices[self.current_device_index]
        self.selected_device = device
        
        # Save configuration
        try:
            subprocess.run(
                [self.script_path, "save_config", device],
                capture_output=True,
                timeout=5
            )
        except Exception as e:
            print(f"Error saving config: {e}")
        
        # Show options page
        self.stack.set_visible_child_name("options")
        
    def on_set_hotkey_clicked(self, button):
        """Start hotkey capture process"""
        if self.session_type != "x11":
            return
            
        # Show hotkey capture page
        self.stack.set_visible_child_name("hotkey")
        self.capture_spinner.start()
        self.capture_status.set_label(_("Launching capture window..."))
        
        # Start capture in background
        GLib.timeout_add(500, self.start_hotkey_capture)
        
    def start_hotkey_capture(self):
        """Start the xbindkeys capture process"""
        try:
            # Run capture command
            result = subprocess.run(
                [self.script_path, "capture_hotkey"],
                capture_output=True,
                text=True,
                timeout=35
            )
            
            captured = result.stdout.strip()
            
            if captured:
                # Parse the keycode (format: "keycode + modifiers")
                self.captured_keycode = captured
                self.capture_status.set_label(_("Key captured!"))
                
                # Save the hotkey
                subprocess.run(
                    [self.script_path, "set_hotkey", captured, captured],
                    capture_output=True,
                    timeout=5
                )
                
                # Update hotkey label
                self.hotkey_label.set_label(captured[:30] + "..." if len(captured) > 30 else captured)
                
                # Go back to options
                GLib.timeout_add(1000, lambda: (self.stack.set_visible_child_name("options"), False)[1])
            else:
                self.capture_status.set_label(_("No key detected"))
                GLib.timeout_add(1500, lambda: (self.stack.set_visible_child_name("options"), False)[1])
                
        except subprocess.TimeoutExpired:
            self.capture_status.set_label(_("Timeout - no key pressed"))
            GLib.timeout_add(1500, lambda: (self.stack.set_visible_child_name("options"), False)[1])
        except Exception as e:
            print(f"Error capturing hotkey: {e}")
            self.capture_status.set_label(_("Error capturing hotkey"))
            GLib.timeout_add(1500, lambda: (self.stack.set_visible_child_name("options"), False)[1])
        finally:
            self.capture_spinner.stop()
        
        return False
        
    def on_cancel_hotkey_capture(self, button):
        """Cancel hotkey capture"""
        self.capture_spinner.stop()
        self.stack.set_visible_child_name("options")
        
    def on_finish_clicked(self, button):
        """Finish configuration and apply settings"""
        # Apply xmodmap if enabled
        if self.xmodmap_row.get_active() and self.session_type == "x11":
            try:
                subprocess.run(
                    [self.script_path, "set_xmodmap", "true"],
                    capture_output=True,
                    timeout=5
                )
            except Exception as e:
                print(f"Error setting xmodmap: {e}")
        
        # Apply autostart
        if self.autostart_row.get_active():
            try:
                subprocess.run(
                    [self.script_path, "toggle", "true"],
                    capture_output=True,
                    timeout=10
                )
            except Exception as e:
                print(f"Error enabling autostart: {e}")
        
        # Update success page
        device_display = self.selected_device
        if device_display.startswith("xset:"):
            device_display = device_display.replace("xset:", "LED #")
        self.saved_device_label.set_label(_("Device: {}").format(device_display))
        
        options_list = []
        if self.autostart_row.get_active():
            options_list.append(_("Autostart enabled"))
        if self.xmodmap_row.get_active() and self.session_type == "x11":
            options_list.append(_("Scroll Lock fix applied"))
        if self.hotkey_label.get_label() != _("Not set"):
            options_list.append(_("Hotkey configured"))
            
        self.options_summary.set_label("\n".join(options_list) if options_list else _("No additional options"))
        
        # Show success page
        self.stack.set_visible_child_name("success")
        
    def on_done_clicked(self, button):
        """Configuration complete - close dialog"""
        self.configuration_completed = True
        if self.on_complete_callback:
            self.on_complete_callback(True)
        
        self.close()
        
    def on_close_no_device(self, button):
        """Close when no device found"""
        # Mark as completed (failed, but intentionally closed)
        self.configuration_completed = True
        if self.on_complete_callback:
            self.on_complete_callback(False)
        
        self.close()
    
    def on_dialog_closed(self, dialog):
        """Handle dialog close - ensure callback is called if not completed"""
        if not self.configuration_completed:
            # Dialog was closed without completing (cancel, X button, etc.)
            # Turn off any device that was being tested
            if self.devices and self.current_device_index < len(self.devices):
                device = self.devices[self.current_device_index]
                try:
                    subprocess.run(
                        [self.script_path, "test_off", device],
                        capture_output=True,
                        timeout=5
                    )
                except:
                    pass
            
            # Call callback with False to revert switch
            if self.on_complete_callback:
                self.on_complete_callback(False)


class LEDControlDialog(Adw.Dialog):
    """Quick control dialog for already configured LED"""
    
    def __init__(self, parent_window, script_path):
        super().__init__()
        self.parent_window = parent_window
        self.script_path = script_path
        self.led_is_on = False
        
        self.set_title(_("LED Control"))
        self.set_content_width(350)
        self.set_content_height(300)
        
        self.setup_ui()
        self.load_current_state()
        
    def setup_ui(self):
        """Build the dialog UI"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_child(main_box)
        
        # Header Bar
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(True)
        header.set_show_start_title_buttons(False)
        main_box.append(header)
        
        # Settings button
        settings_btn = Gtk.Button()
        settings_btn.set_icon_name("emblem-system-symbolic")
        settings_btn.set_tooltip_text(_("Reconfigure"))
        settings_btn.connect("clicked", self.on_reconfigure_clicked)
        header.pack_end(settings_btn)
        
        # Content
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_top(24)
        content.set_margin_bottom(24)
        content.set_margin_start(24)
        content.set_margin_end(24)
        content.set_valign(Gtk.Align.CENTER)
        content.set_vexpand(True)
        main_box.append(content)
        
        # LED icon (changes based on state)
        self.led_icon = Gtk.Image.new_from_icon_name("keyboard-brightness-symbolic")
        self.led_icon.set_pixel_size(80)
        self.led_icon.add_css_class("dim-label")
        content.append(self.led_icon)
        
        # Status label
        self.status_label = Gtk.Label(label=_("LED is OFF"))
        self.status_label.add_css_class("title-2")
        content.append(self.status_label)
        
        # Device info
        self.device_info = Gtk.Label(label="")
        self.device_info.add_css_class("caption")
        self.device_info.add_css_class("dim-label")
        content.append(self.device_info)
        
        # Toggle button
        self.toggle_btn = Gtk.Button(label=_("Turn ON"))
        self.toggle_btn.add_css_class("suggested-action")
        self.toggle_btn.add_css_class("pill")
        self.toggle_btn.set_halign(Gtk.Align.CENTER)
        self.toggle_btn.set_margin_top(24)
        self.toggle_btn.connect("clicked", self.on_toggle_clicked)
        content.append(self.toggle_btn)
        
    def load_current_state(self):
        """Load current LED state from script"""
        try:
            result = subprocess.run(
                [self.script_path, "get_info"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            info = {}
            for line in result.stdout.strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    info[key] = value
            
            device_id = info.get("ID", "")
            method = info.get("METHOD", "")
            
            self.device_info.set_label(f"{method}: {device_id}")
            
        except Exception as e:
            print(f"Error loading state: {e}")
            
    def on_toggle_clicked(self, button):
        """Toggle LED state"""
        try:
            subprocess.run(
                [self.script_path, "led_toggle"],
                capture_output=True,
                timeout=5
            )
            
            # Toggle UI state
            self.led_is_on = not self.led_is_on
            self.update_ui_state()
            
        except Exception as e:
            print(f"Error toggling LED: {e}")
            
    def update_ui_state(self):
        """Update UI based on LED state"""
        if self.led_is_on:
            self.led_icon.remove_css_class("dim-label")
            self.led_icon.add_css_class("accent")
            self.status_label.set_label(_("LED is ON"))
            self.toggle_btn.set_label(_("Turn OFF"))
            self.toggle_btn.remove_css_class("suggested-action")
            self.toggle_btn.add_css_class("destructive-action")
        else:
            self.led_icon.remove_css_class("accent")
            self.led_icon.add_css_class("dim-label")
            self.status_label.set_label(_("LED is OFF"))
            self.toggle_btn.set_label(_("Turn ON"))
            self.toggle_btn.remove_css_class("destructive-action")
            self.toggle_btn.add_css_class("suggested-action")
            
    def on_reconfigure_clicked(self, button):
        """Open reconfiguration dialog"""
        # Reset config and show main dialog
        try:
            subprocess.run(
                [self.script_path, "reset"],
                capture_output=True,
                timeout=5
            )
        except:
            pass
        
        self.close()
        
        # Show config dialog
        dialog = KeyboardLEDDialog(self.parent_window, self.script_path)
        dialog.present(self.parent_window)
