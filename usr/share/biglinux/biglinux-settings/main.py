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
from performance_page import PerformancePage
from preload_page import PreloadPage
from system_page import SystemPage
from usability_page import UsabilityPage

APP_VERSION = "25.02.23"
APP_ID = "br.com.biglinux-settings"
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
        super().__init__(application_id=APP_ID)
        GLib.set_prgname(APP_ID)
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.window = BiglinuxSettingsWindow(application=app)
        self.window.present()


class BiglinuxSettingsWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title(_("BigLinux Settings"))

        saved_size = self._load_window_config()
        width = saved_size.get("width", 1000)
        height = saved_size.get("height", 700)
        self.set_default_size(width, height)

        icon_theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        icon_theme.add_search_path(ICONS_DIR)

        self.pages_config = []
        self.is_searching = False
        self.current_page_id = None
        self._synced_pages = set()
        self.load_css()
        self.setup_ui()

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

    def setup_ui(self):
        # Toast overlay as root
        self.toast_overlay = Adw.ToastOverlay()
        self.set_content(self.toast_overlay)

        # OverlaySplitView for modern sidebar + content layout
        self.split_view = Adw.OverlaySplitView()
        self.split_view.set_min_sidebar_width(260)
        self.split_view.set_max_sidebar_width(320)
        self.split_view.set_sidebar_width_fraction(0.32)
        self.toast_overlay.set_child(self.split_view)

        # === SIDEBAR ===
        sidebar_toolbar = Adw.ToolbarView()

        sidebar_header = Adw.HeaderBar()
        sidebar_header.set_show_end_title_buttons(False)

        # App icon on the left
        app_icon = Gtk.Image.new_from_icon_name("biglinux-settings")
        app_icon.set_pixel_size(20)
        sidebar_header.pack_start(app_icon)

        # Centered title
        title_label = Gtk.Label(label=_("BigLinux Settings"))
        title_label.add_css_class("heading")
        sidebar_header.set_title_widget(title_label)

        sidebar_toolbar.add_top_bar(sidebar_header)

        # Scrollable sidebar content
        sidebar_scroll = Gtk.ScrolledWindow()
        sidebar_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sidebar_scroll.set_vexpand(True)

        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        sidebar_box.set_margin_start(12)
        sidebar_box.set_margin_end(12)
        sidebar_box.set_margin_top(6)
        sidebar_box.set_margin_bottom(12)

        # Navigation ListBox with built-in selection
        self.sidebar_list = Gtk.ListBox()
        self.sidebar_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.sidebar_list.add_css_class("navigation-sidebar")
        self.sidebar_list.connect("row-selected", self.on_sidebar_row_selected)
        sidebar_box.append(self.sidebar_list)

        sidebar_scroll.set_child(sidebar_box)
        sidebar_toolbar.set_content(sidebar_scroll)

        self.split_view.set_sidebar(sidebar_toolbar)

        # === CONTENT ===
        content_toolbar = Adw.ToolbarView()

        content_header = Adw.HeaderBar()
        content_header.set_show_start_title_buttons(False)

        # Search entry centered
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text(_("Search..."))
        self.search_entry.set_hexpand(False)
        self.search_entry.set_width_chars(30)
        self.search_entry.connect("search-changed", self.on_search_changed)
        content_header.set_title_widget(self.search_entry)

        content_toolbar.add_top_bar(content_header)

        # === SEARCH RESULTS ===
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

        self.search_results_group = Adw.PreferencesGroup()
        self.search_results_box.append(self.search_results_group)

        self.reparented_rows = []

        # === PAGE STACK ===
        self.page_stack = Gtk.Stack()
        self.page_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.page_stack.set_transition_duration(200)
        self.page_stack.set_vexpand(True)

        # Content wrapper to switch between pages and search results
        self.content_wrapper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.content_wrapper.append(self.page_stack)
        self.content_wrapper.append(self.search_results_scroll)
        content_toolbar.set_content(self.content_wrapper)

        self.split_view.set_content(content_toolbar)

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
                "label": _("Performance"),
                "icon": "performance-symbolic",
                "id": "performance",
                "class": PerformancePage,
            },
        ]

        for page_cfg in self.pages_config:
            # Sidebar navigation row
            row = Gtk.ListBoxRow()
            row.page_id = page_cfg["id"]

            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            box.set_margin_top(8)
            box.set_margin_bottom(8)
            box.set_margin_start(8)
            box.set_margin_end(8)

            icon_path = os.path.join(ICONS_DIR, f"{page_cfg['icon']}.svg")
            gfile = Gio.File.new_for_path(icon_path)
            img = Gtk.Image.new_from_gicon(Gio.FileIcon.new(gfile))
            img.set_pixel_size(20)
            img.add_css_class("symbolic-icon")
            box.append(img)

            lbl = Gtk.Label(label=page_cfg["label"], xalign=0, hexpand=True)
            box.append(lbl)

            row.set_child(box)
            self.sidebar_list.append(row)

            # Page instance (no sync in __init__ — deferred to first show)
            page_instance = page_cfg["class"](self)
            page_cfg["instance"] = page_instance
            self.page_stack.add_named(page_instance, page_cfg["id"])

        # Select first page
        first_row = self.sidebar_list.get_row_at_index(0)
        if first_row:
            self.sidebar_list.select_row(first_row)

    def on_sidebar_row_selected(self, listbox, row):
        if row is None or self.is_searching:
            return
        self.current_page_id = row.page_id
        self._show_single_page(row.page_id)

    def _show_single_page(self, page_id):
        """Show only one page via Gtk.Stack (normal mode)."""
        self._restore_reparented_rows()

        self.search_results_scroll.set_visible(False)
        self.page_stack.set_visible(True)
        self.page_stack.set_visible_child_name(page_id)

        # Reset filter on visible page
        for page_cfg in self.pages_config:
            instance = page_cfg.get("instance")
            if instance and hasattr(instance, "set_search_mode"):
                instance.set_search_mode(False)
            if (
                page_cfg["id"] == page_id
                and instance
                and hasattr(instance, "filter_rows")
            ):
                instance.filter_rows("")

        # Lazy sync: only sync a page on first visit
        if page_id not in self._synced_pages:
            for page_cfg in self.pages_config:
                if page_cfg["id"] == page_id:
                    instance = page_cfg["instance"]
                    if hasattr(instance, "sync_all_switches_async"):
                        instance.sync_all_switches_async()
                    self._synced_pages.add(page_id)
                    break

    def _show_search_results(self, search_text):
        """Show search results in a single compact container."""
        self._restore_reparented_rows()

        self.page_stack.set_visible(False)
        self.search_results_scroll.set_visible(True)

        # Ensure all pages are synced for accurate search results
        for page_cfg in self.pages_config:
            page_id = page_cfg["id"]
            if page_id not in self._synced_pages:
                instance = page_cfg["instance"]
                if hasattr(instance, "sync_all_switches_async"):
                    instance.sync_all_switches_async()
                self._synced_pages.add(page_id)

        for page_cfg in self.pages_config:
            instance = page_cfg.get("instance")
            if instance and hasattr(instance, "get_matching_rows"):
                matching_rows = instance.get_matching_rows(search_text)
                for row, original_parent in matching_rows:
                    self.reparented_rows.append((row, original_parent))
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

        if len(search_text) < 2:
            self.is_searching = False
            self.sidebar_list.set_sensitive(True)
            self._show_single_page(self.current_page_id or self.pages_config[0]["id"])
        else:
            self.is_searching = True
            self.sidebar_list.set_sensitive(False)
            self._show_search_results(search_text)

    def show_toast(self, message):
        toast = Adw.Toast(title=message, timeout=3)
        self.toast_overlay.add_toast(toast)


def main():
    app = BiglinuxSettingsApp()
    return app.run()


if __name__ == "__main__":
    main()
