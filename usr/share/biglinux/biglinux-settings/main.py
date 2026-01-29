#!/usr/bin/env python3
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gdk", "4.0")
import gettext
import locale
import os

from gi.repository import Adw, Gdk, Gio, Gtk
from preload_page import PreloadPage
from system_page import SystemPage
from usability_page import UsabilityPage
from devices_page import DevicesPage
from ai_page import AIPage
from docker_page import DockerPage
from performance_games_page import PerformanceGamesPage


DOMAIN = "biglinux-settings"
LOCALE_DIR = "/usr/share/locale"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICONS_DIR = os.path.join(BASE_DIR, "icons")

locale.setlocale(locale.LC_ALL, "")
locale.bindtextdomain(DOMAIN, LOCALE_DIR)
locale.textdomain(DOMAIN)

gettext.bindtextdomain(DOMAIN, LOCALE_DIR)
gettext.textdomain(DOMAIN)
_ = gettext.gettext


class BiglinuxSettingsApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="org.biglinux.biglinux-settings")
        style_manager = Adw.StyleManager.get_default()
        style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.window = CustomWindow(application=app)
        self.window.present()


class SystemSettingsWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("BigLinux Settings")
        self.set_default_size(1000, 860)
        icon_theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        icon_theme.add_search_path(ICONS_DIR)
        self.load_css()
        self.setup_ui()

    def load_css(self):
        provider = Gtk.CssProvider()
        css = """
        .sidebar-container {
            background-color: @card_bg_color;
            border-right: 1px solid alpha(@window_fg_color, 0.05);
        }
        .content-area {
            background-color: @window_bg_color;
        }
        .symbolic-icon {
            -gtk-icon-filter: -gtk-recolor();
            color: @window_fg_color;
        }
        .sidebar-button {
            padding: 8px;
            border-radius: 8px;
        }
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
        """
        provider.load_from_string(css)
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def create_sidebar_button(self, label_text, icon_name, stack_name, view_stack):
        btn = Gtk.Button()
        btn.add_css_class("flat")
        btn.add_css_class("sidebar-button")

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        icon_path = os.path.join(ICONS_DIR, f"{icon_name}.svg")
        gfile = Gio.File.new_for_path(icon_path)
        icon = Gio.FileIcon.new(gfile)

        img = Gtk.Image.new_from_gicon(icon)
        img.set_pixel_size(24)
        img.add_css_class("symbolic-icon")

        lbl = Gtk.Label(label=label_text, xalign=0)

        box.append(img)
        box.append(lbl)

        btn.set_child(box)
        btn.connect("clicked", lambda _: view_stack.set_visible_child_name(stack_name))
        return btn

    def setup_ui(self):
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)

        header_bar = Adw.HeaderBar()
        main_box.append(header_bar)

        # Body Container (Sidebar + Content)
        content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        main_box.append(content_box)

        view_stack = Adw.ViewStack()
        view_stack.add_css_class("content-area")
        view_stack.set_hexpand(True)
        view_stack.set_vexpand(True)

        # Sidebar settings
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_propagate_natural_width(True)
        scrolled.add_css_class("sidebar-container")

        side_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        side_box.set_margin_start(12)
        side_box.set_margin_end(12)
        side_box.set_margin_top(22)
        side_box.set_margin_bottom(12)
        side_box.set_size_request(220, -1)

        scrolled.set_child(side_box)
        content_box.append(scrolled)
        content_box.append(view_stack)

        ## Sidebar Buttons ##
        pages_config = [
            {"label": _("System"),      "icon": "system-symbolic",      "id": "system",     "class": SystemPage},
            {"label": _("Usability"),   "icon": "usability-symbolic",   "id": "usability",  "class": UsabilityPage},
            {"label": _("PreLoad"),     "icon": "preload-symbolic",     "id": "preload",    "class": PreloadPage},
            {"label": _("Devices"),     "icon": "devices-symbolic",     "id": "devices",    "class": DevicesPage},
            {"label": _("A.I."),        "icon": "ai-symbolic",          "id": "ai",         "class": AIPage},
            {"label": _("Docker"),      "icon": "docker-symbolic",      "id": "docker",     "class": DockerPage},
            {"label": _("Performance and Games"),       "icon": "games-symbolic",       "id": "perf_games", "class": PerformanceGamesPage},
        ]

        # Loop to automatically create buttons and pages
        for page in pages_config:
            # Cria o botão na barra lateral
            btn = self.create_sidebar_button(page["label"], page["icon"], page["id"], view_stack)
            side_box.append(btn)

            # Cria a instância da página e adiciona ao stack
            page_instance = page["class"](self)
            view_stack.add_titled(page_instance, page["id"], page["label"])

class CustomWindow(SystemSettingsWindow):
    def __init__(self, **kwargs):
        self.toast_overlay = Adw.ToastOverlay()
        super().__init__(**kwargs)
        content = self.get_content()
        self.set_content(None)
        self.toast_overlay.set_child(content)
        self.set_content(self.toast_overlay)

    def show_toast(self, message):
        toast = Adw.Toast(title=message, timeout=3)
        self.toast_overlay.add_toast(toast)


def main():
    app = BiglinuxSettingsApp()
    return app.run()


if __name__ == "__main__":
    main()
