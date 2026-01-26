from base_page import BaseSettingsPage
import locale
import gettext

# Set up gettext for application localization.
DOMAIN = "biglinux-settings"
LOCALE_DIR = "/usr/share/locale"

locale.setlocale(locale.LC_ALL, "")
locale.bindtextdomain(DOMAIN, LOCALE_DIR)
locale.textdomain(DOMAIN)

gettext.bindtextdomain(DOMAIN, LOCALE_DIR)
gettext.textdomain(DOMAIN)
_ = gettext.gettext

class PreloadPage(BaseSettingsPage):
    def __init__(self, main_window, **kwargs):
        super().__init__(main_window, **kwargs)

        content = self.create_scrolled_content()
        group = self.create_group(
            _("Preload"),
            _("Preload applications into memory to open them faster."),
            "preload"
        )
        content.append(group)

        # List of (Name, Script Name, Icon)
        apps = [
            (_("Firefox"), "firefox", "firefox-symbolic"),
            (_("Brave"), "brave", "brave-symbolic"),
            (_("Chrome"), "chrome", "chrome-symbolic"),
            (_("Chromium"), "chromium", "chromium-symbolic"),
            (_("Librewolf"), "librewolf", "librewolf-symbolic"),
            (_("Palemoon"), "palemoon", "palemoon-symbolic"),
            (_("Opera"), "opera", "opera-symbolic"),
            (_("Libreoffice"), "libreoffice", "libreoffice-symbolic"),
        ]

        for label, script, icon in apps:
            self.create_row(group, label, None, script, icon)

        self.sync_all_switches()
