#!/usr/bin/env python3
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gdk", "4.0")
import gettext
import json
import locale
import os

from ai_page import AIPage
from devices_page import DevicesPage
from docker_page import DockerPage
from gi.repository import Adw, Gdk, Gio, GLib, Gtk
from performance_games_page import PerformanceGamesPage
from preload_page import PreloadPage
from system_page import SystemPage
from usability_page import UsabilityPage

DOMAIN = "biglinux-settings"
LOCALE_DIR = "/usr/share/locale"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICONS_DIR = os.path.join(BASE_DIR, "icons")
CONFIG_DIR = os.path.expanduser("~/.config/biglinux-settings")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

locale.setlocale(locale.LC_ALL, "")
locale.bindtextdomain(DOMAIN, LOCALE_DIR)
locale.textdomain(DOMAIN)

gettext.bindtextdomain(DOMAIN, LOCALE_DIR)
gettext.textdomain(DOMAIN)
_ = gettext.gettext


class BiglinuxSettingsApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="org.biglinux.biglinux-settings")
        GLib.set_prgname("biglinux-settings")
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.window = BiglinuxSettingsWindow(application=app)
        self.window.present()


class BiglinuxSettingsWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title(_("BigLinux Settings"))

        # Load saved window size or use defaults
        saved_size = self._load_window_config()
        width = saved_size.get("width", 1000)
        height = saved_size.get("height", 700)
        self.set_default_size(width, height)

        icon_theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        icon_theme.add_search_path(ICONS_DIR)

        self.sidebar_buttons = []
        self.pages_config = []
        self.is_searching = False
        self.current_page_id = None
        self.load_css()
        self.setup_ui()

        # Connect close signal to save window size
        self.connect("close-request", self._on_close_request)

    def _load_window_config(self):
        """Load window configuration from JSON file."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                print(f"Error loading window config: {e}")
        return {}

    def _save_window_config(self):
        """Save window configuration to JSON file."""
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            width = self.get_width()
            height = self.get_height()
            config = {"width": width, "height": height}
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except OSError as e:
            print(f"Error saving window config: {e}")

    def _on_close_request(self, window):
        """Handle window close request - save configuration."""
        self._save_window_config()
        return False  # Allow window to close

    def load_css(self):
        self.css_provider = Gtk.CssProvider()
        css_path = os.path.join(BASE_DIR, "styles.css")
        self.css_provider.load_from_path(css_path)
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(),
            self.css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def create_sidebar_button(self, label_text, icon_name, stack_name):
        btn = Gtk.Button()
        btn.add_css_class("flat")
        btn.add_css_class("sidebar-button")
        btn.stack_name = stack_name
        btn.label_text = label_text

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        icon_path = os.path.join(ICONS_DIR, f"{icon_name}.svg")
        gfile = Gio.File.new_for_path(icon_path)
        icon = Gio.FileIcon.new(gfile)

        img = Gtk.Image.new_from_gicon(icon)
        img.set_pixel_size(24)
        img.add_css_class("symbolic-icon")

        lbl = Gtk.Label(label=label_text, xalign=0)
        lbl.set_hexpand(True)

        box.append(img)
        box.append(lbl)

        btn.set_child(box)
        btn.connect("clicked", self.on_sidebar_button_clicked)
        return btn

    def on_sidebar_button_clicked(self, btn):
        if self.is_searching:
            return
        self.current_page_id = btn.stack_name
        self._show_single_page(btn.stack_name)
        for b in self.sidebar_buttons:
            b.remove_css_class("selected")
        btn.add_css_class("selected")

    def setup_ui(self):
        # Toast overlay as root
        self.toast_overlay = Adw.ToastOverlay()
        self.set_content(self.toast_overlay)

        # NavigationSplitView for modern sidebar + content layout
        self.split_view = Adw.NavigationSplitView()
        self.toast_overlay.set_child(self.split_view)

        # === SIDEBAR ===
        sidebar_toolbar = Adw.ToolbarView()
        sidebar_header = Adw.HeaderBar()
        sidebar_header.set_title_widget(Adw.WindowTitle.new(_("BigLinux Settings"), ""))
        sidebar_toolbar.add_top_bar(sidebar_header)

        sidebar_scroll = Gtk.ScrolledWindow()
        sidebar_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sidebar_scroll.set_vexpand(True)

        self.sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.sidebar_box.set_margin_start(12)
        self.sidebar_box.set_margin_end(12)
        self.sidebar_box.set_margin_top(12)
        self.sidebar_box.set_margin_bottom(12)
        sidebar_scroll.set_child(self.sidebar_box)
        sidebar_toolbar.set_content(sidebar_scroll)

        sidebar_page = Adw.NavigationPage.new(sidebar_toolbar, _("Categories"))
        self.split_view.set_sidebar(sidebar_page)

        # === CONTENT ===
        content_toolbar = Adw.ToolbarView()
        content_header = Adw.HeaderBar()

        # Search entry in header (centered)
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text(_("Search..."))
        self.search_entry.set_hexpand(False)
        self.search_entry.set_width_chars(30)
        self.search_entry.connect("search-changed", self.on_search_changed)
        content_header.set_title_widget(self.search_entry)
        content_toolbar.add_top_bar(content_header)

        # === CREATE SEARCH RESULTS CONTAINER ===
        self.search_results_scroll = Gtk.ScrolledWindow()
        self.search_results_scroll.set_policy(
            Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC
        )
        self.search_results_scroll.set_vexpand(True)
        self.search_results_scroll.set_visible(False)

        self.search_results_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=0,
            margin_top=12,
            margin_bottom=12,
            margin_start=20,
            margin_end=20,
        )
        self.search_results_scroll.set_child(self.search_results_box)

        # Search results group (single group for all results)
        self.search_results_group = Adw.PreferencesGroup()
        self.search_results_box.append(self.search_results_group)

        # Track original parents of rows for restoration
        self.reparented_rows = []

        # ScrolledWindow with all pages stacked vertically
        self.content_scroll = Gtk.ScrolledWindow()
        self.content_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.content_scroll.set_vexpand(True)

        self.pages_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.content_scroll.set_child(self.pages_box)

        # Content wrapper to switch between pages and search results
        self.content_wrapper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.content_wrapper.append(self.content_scroll)
        self.content_wrapper.append(self.search_results_scroll)
        content_toolbar.set_content(self.content_wrapper)

        content_page = Adw.NavigationPage.new(content_toolbar, _("Settings"))
        self.split_view.set_content(content_page)

        # === CREATE PAGES ===
        self.pages_config = [
            {
                "label": _("System"),
                "icon": "system-symbolic",
                "id": "system",
                "class": SystemPage,
            },
            {
                "label": _("Usability"),
                "icon": "usability-symbolic",
                "id": "usability",
                "class": UsabilityPage,
            },
            {
                "label": _("PreLoad"),
                "icon": "preload-symbolic",
                "id": "preload",
                "class": PreloadPage,
            },
            {
                "label": _("Devices"),
                "icon": "devices-symbolic",
                "id": "devices",
                "class": DevicesPage,
            },
            {
                "label": _("A.I."),
                "icon": "ai-symbolic",
                "id": "ai",
                "class": AIPage,
            },
            {
                "label": _("Docker"),
                "icon": "docker-geral-symbolic",
                "id": "docker",
                "class": DockerPage,
            },
            {
                "label": _("Performance and Games"),
                "icon": "games-symbolic",
                "id": "perf_games",
                "class": PerformanceGamesPage,
            },
        ]

        for page in self.pages_config:
            # Sidebar button
            btn = self.create_sidebar_button(page["label"], page["icon"], page["id"])
            self.sidebar_box.append(btn)
            self.sidebar_buttons.append(btn)

            # Page instance
            page_instance = page["class"](self)
            page["instance"] = page_instance
            self.pages_box.append(page_instance)

        # Select and show first page
        if self.sidebar_buttons:
            self.sidebar_buttons[0].add_css_class("selected")
            self.current_page_id = self.pages_config[0]["id"]
            self._show_single_page(self.current_page_id)

    def _show_single_page(self, page_id):
        """Show only one page (normal mode)."""
        # Restore any reparented rows first
        self._restore_reparented_rows()

        # Hide search results, show pages
        self.search_results_scroll.set_visible(False)
        self.content_scroll.set_visible(True)

        for page in self.pages_config:
            instance = page["instance"]
            is_current = page["id"] == page_id
            instance.set_visible(is_current)
            if hasattr(instance, "set_search_mode"):
                instance.set_search_mode(False)
            if is_current and hasattr(instance, "filter_rows"):
                instance.filter_rows("")

    def _show_search_results(self, search_text):
        """Show search results in a single compact container."""
        # Restore any previously reparented rows first
        self._restore_reparented_rows()

        # Hide pages, show search results
        self.content_scroll.set_visible(False)
        self.search_results_scroll.set_visible(True)

        # Collect matching rows from all pages
        for page in self.pages_config:
            instance = page.get("instance")
            if instance and hasattr(instance, "get_matching_rows"):
                matching_rows = instance.get_matching_rows(search_text)
                for row, original_parent in matching_rows:
                    # Store original parent for restoration
                    self.reparented_rows.append((row, original_parent))
                    # Reparent to search results
                    original_parent.remove(row)
                    self.search_results_group.add(row)

    def _restore_reparented_rows(self):
        """Restore rows to their original parents."""
        for row, original_parent in self.reparented_rows:
            self.search_results_group.remove(row)
            original_parent.add(row)
        self.reparented_rows = []

    def on_search_changed(self, entry):
        search_text = entry.get_text().lower().strip()

        # Require minimum 2 characters for search
        if len(search_text) < 2:
            # Exit search mode
            self.is_searching = False
            for btn in self.sidebar_buttons:
                btn.set_sensitive(True)
            self._show_single_page(self.current_page_id or self.pages_config[0]["id"])
        else:
            # Enter search mode
            self.is_searching = True
            for btn in self.sidebar_buttons:
                btn.set_sensitive(False)
            self._show_search_results(search_text)

    def show_toast(self, message):
        toast = Adw.Toast(title=message, timeout=3)
        self.toast_overlay.add_toast(toast)


def main():
    app = BiglinuxSettingsApp()
    return app.run()


if __name__ == "__main__":
    main()
