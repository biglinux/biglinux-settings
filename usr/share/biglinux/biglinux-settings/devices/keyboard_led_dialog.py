#!/usr/bin/env python3
"""
Keyboard LED Configuration Dialog
GTK4/Adwaita dialog for configuring keyboard LED device
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
import subprocess
import os
import gettext

DOMAIN = 'biglinux-settings'
LOCALE_DIR = '/usr/share/locale'
gettext.bindtextdomain(DOMAIN, LOCALE_DIR)
gettext.textdomain(DOMAIN)
_ = gettext.gettext


class KeyboardLEDDialog(Adw.Dialog):
    """Dialog for configuring keyboard LED device"""
    
    def __init__(self, parent_window, script_path, on_complete_callback=None):
        super().__init__()
        self.parent_window = parent_window
        self.script_path = script_path
        self.on_complete_callback = on_complete_callback
        self.devices = []
        self.current_device_index = 0
        self.selected_device = None
        
        self.set_title(_("Keyboard LED Configuration"))
        self.set_content_width(450)
        self.set_content_height(350)
        
        self.setup_ui()
        
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
        
        # Content
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_top(24)
        content.set_margin_bottom(24)
        content.set_margin_start(24)
        content.set_margin_end(24)
        main_box.append(content)
        
        # Stack for different views
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_vexpand(True)
        content.append(self.stack)
        
        # Page 1: Welcome/Start
        self.create_welcome_page()
        
        # Page 2: Testing devices
        self.create_testing_page()
        
        # Page 3: Success
        self.create_success_page()
        
        # Page 4: No devices found
        self.create_no_devices_page()
        
    def create_welcome_page(self):
        """Create the welcome/introduction page"""
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        page.set_valign(Gtk.Align.CENTER)
        
        # Icon
        icon = Gtk.Image.new_from_icon_name("keyboard-brightness-symbolic")
        icon.set_pixel_size(64)
        icon.add_css_class("dim-label")
        page.append(icon)
        
        # Title
        title = Gtk.Label(label=_("Configure Keyboard LED"))
        title.add_css_class("title-1")
        page.append(title)
        
        # Description
        desc = Gtk.Label(
            label=_("We will test the available LED devices on your system.\nThe script will turn on each device one by one so you can identify which one is your keyboard LED.")
        )
        desc.set_wrap(True)
        desc.set_justify(Gtk.Justification.CENTER)
        desc.add_css_class("dim-label")
        page.append(desc)
        
        # Start button
        start_btn = Gtk.Button(label=_("Start Configuration"))
        start_btn.add_css_class("suggested-action")
        start_btn.add_css_class("pill")
        start_btn.set_halign(Gtk.Align.CENTER)
        start_btn.connect("clicked", self.on_start_clicked)
        page.append(start_btn)
        
        self.stack.add_named(page, "welcome")
        
    def create_testing_page(self):
        """Create the device testing page"""
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        page.set_valign(Gtk.Align.CENTER)
        
        # Icon
        icon = Gtk.Image.new_from_icon_name("dialog-question-symbolic")
        icon.set_pixel_size(48)
        icon.add_css_class("dim-label")
        page.append(icon)
        
        # Title
        title = Gtk.Label(label=_("Did the keyboard LED turn on?"))
        title.add_css_class("title-2")
        page.append(title)
        
        # Device name label
        self.device_label = Gtk.Label(label="")
        self.device_label.add_css_class("caption")
        self.device_label.add_css_class("dim-label")
        page.append(self.device_label)
        
        # Progress indicator
        self.progress_label = Gtk.Label(label="")
        self.progress_label.add_css_class("caption")
        page.append(self.progress_label)
        
        # Buttons
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.CENTER)
        page.append(btn_box)
        
        no_btn = Gtk.Button(label=_("No"))
        no_btn.add_css_class("destructive-action")
        no_btn.add_css_class("pill")
        no_btn.connect("clicked", self.on_no_clicked)
        btn_box.append(no_btn)
        
        yes_btn = Gtk.Button(label=_("Yes, this is it!"))
        yes_btn.add_css_class("suggested-action")
        yes_btn.add_css_class("pill")
        yes_btn.connect("clicked", self.on_yes_clicked)
        btn_box.append(yes_btn)
        
        self.stack.add_named(page, "testing")
        
    def create_success_page(self):
        """Create the success page"""
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        page.set_valign(Gtk.Align.CENTER)
        
        # Icon
        icon = Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
        icon.set_pixel_size(64)
        icon.add_css_class("success")
        page.append(icon)
        
        # Title
        title = Gtk.Label(label=_("Configuration Complete!"))
        title.add_css_class("title-1")
        page.append(title)
        
        # Device saved label
        self.saved_device_label = Gtk.Label(label="")
        self.saved_device_label.add_css_class("caption")
        self.saved_device_label.add_css_class("dim-label")
        page.append(self.saved_device_label)
        
        # Description
        desc = Gtk.Label(
            label=_("Your keyboard LED will now turn on automatically when the system starts.")
        )
        desc.set_wrap(True)
        desc.set_justify(Gtk.Justification.CENTER)
        desc.add_css_class("dim-label")
        page.append(desc)
        
        # Close button
        close_btn = Gtk.Button(label=_("Done"))
        close_btn.add_css_class("suggested-action")
        close_btn.add_css_class("pill")
        close_btn.set_halign(Gtk.Align.CENTER)
        close_btn.connect("clicked", self.on_done_clicked)
        page.append(close_btn)
        
        self.stack.add_named(page, "success")
        
    def create_no_devices_page(self):
        """Create the no devices found page"""
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        page.set_valign(Gtk.Align.CENTER)
        
        # Icon
        icon = Gtk.Image.new_from_icon_name("dialog-error-symbolic")
        icon.set_pixel_size(64)
        icon.add_css_class("error")
        page.append(icon)
        
        # Title
        title = Gtk.Label(label=_("No Compatible Device Found"))
        title.add_css_class("title-1")
        page.append(title)
        
        # Description
        desc = Gtk.Label(
            label=_("Could not find a compatible keyboard LED device.\n\nMake sure your keyboard has LED support and that brightnessctl is installed.")
        )
        desc.set_wrap(True)
        desc.set_justify(Gtk.Justification.CENTER)
        desc.add_css_class("dim-label")
        page.append(desc)
        
        # Close button
        close_btn = Gtk.Button(label=_("Close"))
        close_btn.add_css_class("pill")
        close_btn.set_halign(Gtk.Align.CENTER)
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
        
        # Update labels
        self.device_label.set_label(_("Testing device: {}").format(device))
        self.progress_label.set_label(_("Device {} of {}").format(
            self.current_device_index + 1, 
            len(self.devices)
        ))
        
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
        """User said YES - save this device"""
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
        
        # Update success page
        self.saved_device_label.set_label(_("Saved device: {}").format(device))
        
        # Show success page
        self.stack.set_visible_child_name("success")
        
    def on_done_clicked(self, button):
        """Configuration complete - close and enable autostart"""
        # Enable autostart via toggle
        try:
            subprocess.run(
                [self.script_path, "toggle", "true"],
                capture_output=True,
                timeout=10
            )
        except Exception as e:
            print(f"Error enabling autostart: {e}")
        
        if self.on_complete_callback:
            self.on_complete_callback(True)
        
        self.close()
        
    def on_close_no_device(self, button):
        """Close when no device found"""
        if self.on_complete_callback:
            self.on_complete_callback(False)
        
        self.close()
