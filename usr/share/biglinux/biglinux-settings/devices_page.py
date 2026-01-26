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

class DevicesPage(BaseSettingsPage):
    def __init__(self, main_window, **kwargs):
        super().__init__(main_window, **kwargs)

        # Create the container (base method)
        content = self.create_scrolled_content()

        # Create the group (base method)
        group = self.create_group(
            _("Devices"),
            _("Manage physical devices."),
            "devices"
        )
        content.append(group)

        # Wifi
        self.create_row(
            group,
            _("Wifi"),
            _("Wifi On"),
            "wifi",
            "wirefi-symbolic"
        )

        # Bluetooth
        self.create_row(
            group,
            _("Bluetooth"),
            _("Bluetooth On."),
            "bluetooth",
            "bluetooth-symbolic"
        )

        # JamesDSP
        self.create_row(
            group,
            _("JamesDSP"),
            _("Advanced audio effects processor that improves sound quality."),
            "jamesdsp",
            "jamesdsp-symbolic"
        )

        # Keyboard LED
        self.create_row(
            group,
            _("Keyboard LED"),
            _("If your keyboard has LED you can enable this feature to turn it on with the system."),
            "keyboard-led",
            "keyboard-led-symbolic"
        )

        # Reverse mouse scrolling
        self.create_row(
            group,
            _("Reverse mouse scrolling"),
            _("Reverse mouse scrolling without restarting the session."),
            "reverse-mouse_scroll",
            "reverse-mouse_scroll-symbolic"
        )

        # Syncs
        self.sync_all_switches()
