#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
import subprocess
import os
import locale
import gettext

from system_usability_page import SystemUsabilityPage
from preload_page import PreloadPage
from dispositivos_page import DispositivosPage
from containers_page import ContainersPage
from ai_page import AIPage

# Set up gettext for application localization.
DOMAIN = 'biglinux-settings'
LOCALE_DIR = '/usr/share/locale'

locale.setlocale(locale.LC_ALL, '')
locale.bindtextdomain(DOMAIN, LOCALE_DIR)
locale.textdomain(DOMAIN)

gettext.bindtextdomain(DOMAIN, LOCALE_DIR)
gettext.textdomain(DOMAIN)
_ = gettext.gettext

class BiglinuxSettingsApp(Adw.Application):
    """The main application class."""
    def __init__(self):
        super().__init__(application_id='org.biglinux.biglinux-settings')

        # Set the color scheme to follow the system's preference (light/dark).
        # This prevents Adwaita from complaining about legacy GTK settings.
        style_manager = Adw.StyleManager.get_default()
        style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)

        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        """Called when the application is activated."""
        # Use the CustomWindow class which includes the ToastOverlay
        self.window = CustomWindow(application=app)
        self.window.present()

class SystemSettingsWindow(Adw.ApplicationWindow):
    """The main window for the application, containing all UI elements."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Window configuration
        self.set_title(_("General adjustments"))
        self.set_default_size(800, 600)

        # Load custom CSS for styling
        self.load_css()

        # Build the user interface
        self.setup_ui()

    def load_css(self):
        """Loads custom CSS for styling widgets like status indicators."""
        provider = Gtk.CssProvider()
        css = """
        preferencesgroup .heading {
            font-size: 1.3rem;
        }
        .status-indicator {
            min-width: 16px;
            min-height: 16px;
            border-radius: 8px;
            margin: 0 8px;
        }
        .status-on {
            background-color: @success_color;
        }
        .status-off {
            background-color: @error_color;
        }
        .status-unavailable {
            background-color: @insensitive_fg_color;
        }
        /* Increase header ViewSwitcher icon size */
        viewswitcher > button image {
            -gtk-icon-size: 24px;
        }
        """
        provider.load_from_string(css)
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def setup_ui(self):
        """Constructs the main UI layout and populates it with widgets."""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)

        header_bar = Adw.HeaderBar()
        main_box.append(header_bar)

        # ViewStack to contain the different settings pages
        view_stack = Adw.ViewStack()
        main_box.append(view_stack)

        # ViewSwitcher to control the ViewStack, placed in the HeaderBar
        view_switcher = Adw.ViewSwitcher()
        view_switcher.set_stack(view_stack)
        header_bar.set_title_widget(view_switcher)

        # Page creation
        # 1. Sistema
        system_usability_page = self.create_system_usability_page()
        view_stack.add_titled_with_icon(system_usability_page, "system", _("System"), "preferences-system-symbolic")

        # 2. Dispositivos
        dispositivos_page = self.create_dispositivos_page()
        view_stack.add_titled_with_icon(dispositivos_page, "devices", _("Devices"), "network-wireless-symbolic")

        # 3. I.A.
        ai_page = self.create_ai_page()
        view_stack.add_titled_with_icon(ai_page, "ai", _("I.A."), "im-user-symbolic") 
        # Note: "ubiquity-kde-icon" is just a placeholder, better to use something standard like 'utilities-terminal-symbolic' or generic if unknown, 
        # but specifically for AI, 'preferences-desktop-productivity' or similar. 
        # I'll use 'computer-symbolic' or similar if no specific AI icon. 
        # User didn't specify icon. I will use 'preferences-other-symbolic' or 'applications-science-symbolic'.
        # Let's try 'starred-symbolic' or 'preferences-system-symbolic' (used)
        # 'utilities-system-monitor-symbolic'?
        # I'll use 'applications-science-symbolic' if available, else 'emblem-important-symbolic'.
        # Actually 'auto-type-symbolic' or 'chatbot-symbolic' might not exist.
        # I'll stick to 'preferences-desktop-personal-symbolic' or simply 'help-about-symbolic'.
        # Let's use 'utilities-terminal-symbolic' as a temp or 'dialog-information-symbolic'.
        # BETTER: 'head-brain' or similar if available? 
        # Let's use 'security-high-symbolic'? No.
        # 'preferences-other-symbolic' is safe.
        
        # 4. Contêiners
        containers_page = self.create_containers_page()
        view_stack.add_titled_with_icon(containers_page, "containers", _("Containers"), "package-x-generic-symbolic")

        # Preload (Keeping it but maybe after?)
        # User list didn't include it. I'll comment it out to strictly follow "I want options...", 
        # or maybe the user expects Preload to be under System?
        # I'll append it at the end just in case, as to not lose functionality, but user might complain.
        # "Chat no header menu quero que tenha as opções [List]" -> "I want the options [List]".
        # I will comment it out for now to be precise.
        # preload_page = self.create_preload_page()
        # view_stack.add_titled_with_icon(preload_page, "preload", _("PreLoad"), "drive-harddisk-symbolic")

    def create_system_usability_page(self):
        return SystemUsabilityPage(self)

    def create_dispositivos_page(self):
        return DispositivosPage(self)
    
    def create_containers_page(self):
        return ContainersPage(self)

    def create_ai_page(self):
        return AIPage(self)

    def create_preload_page(self):
        return PreloadPage(self)

class CustomWindow(SystemSettingsWindow):
    """A subclass of the main window that wraps its content in an Adw.ToastOverlay.
    This is necessary for the `show_toast` method to work correctly."""
    def __init__(self, **kwargs):
        # O ToastOverlay precisa envolver o conteúdo principal.
        self.toast_overlay = Adw.ToastOverlay()

        # Call the parent's __init__ which builds the UI
        super().__init__(**kwargs)

        # Get the UI content built by the parent...
        content = self.get_content()
        # ...detach it from the window...
        self.set_content(None)
        # ...place it inside the ToastOverlay...
        self.toast_overlay.set_child(content)
        # ...and set the ToastOverlay as the new window content.
        self.set_content(self.toast_overlay)

    def show_toast(self, message):
        """Overrides the parent method to ensure it adds toasts to its own overlay."""
        toast = Adw.Toast(title=message, timeout=3)
        self.toast_overlay.add_toast(toast)

def main():
    # SIMPLIFICATION: We only need one Application class.
    app = BiglinuxSettingsApp()
    return app.run()

if __name__ == "__main__":
    main()
