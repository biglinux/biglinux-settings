
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw
from base_page import BaseSettingsPage
import gettext

DOMAIN = 'biglinux-settings'
LOCALE_DIR = '/usr/share/locale'
gettext.bindtextdomain(DOMAIN, LOCALE_DIR)
gettext.textdomain(DOMAIN)
_ = gettext.gettext

class PreloadPage(BaseSettingsPage):
    """A self-contained page for managing Preload tweaks."""
    def populate_content(self, content_box):
        self.usability_group(content_box)

    def usability_group(self, parent):
        """Builds the 'Preload' preferences group."""
        group = Adw.PreferencesGroup()
        group.set_title(_("Preload"))
        group.script_group = "preload"
        group.set_description(_("Preload applications into memory to open them faster."))
        parent.append(group)

        # Create and add the reload button to the group's header
        reload_button = Gtk.Button(
            icon_name="view-refresh-symbolic",
            valign=Gtk.Align.CENTER,
            tooltip_text=_("Reload all statuses")
        )
        reload_button.connect("clicked", self.on_reload_clicked)
        group.set_header_suffix(reload_button)

        # firefox
        self.firefox_switch = self.create_row_with_clickable_link(
            group,
            _("Firefox"),
            None,
            "firefox",
            icon_name="firefox"
        )
        # brave
        self.brave_switch = self.create_row_with_clickable_link(
            group,
            _("Brave"),
            None,
            "brave",
            icon_name="brave-browser"
        )
        # chrome
        self.chrome_switch = self.create_row_with_clickable_link(
            group,
            _("Chrome"),
            None,
            "chrome",
            icon_name="google-chrome"
        )
        # chromium
        self.chromium_switch = self.create_row_with_clickable_link(
            group,
            _("Chromium"),
            None,
            "chromium",
            icon_name="chromium"
        )
        # librewolf
        self.librewolf_switch = self.create_row_with_clickable_link(
            group,
            _("Librewolf"),
            None,
            "librewolf",
            icon_name="librewolf"
        )
        # palemoon
        self.palemoon_switch = self.create_row_with_clickable_link(
            group,
            _("Palemoon"),
            None,
            "palemoon",
            icon_name="palemoon"
        )
        # opera
        self.opera_switch = self.create_row_with_clickable_link(
            group,
            _("Opera"),
            None,
            "opera",
            icon_name="opera"
        )
        # libreoffice
        self.libreoffice_switch = self.create_row_with_clickable_link(
            group,
            _("Libreoffice"),
            None,
            "libreoffice",
            icon_name="libreoffice-startcenter"
        )

