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

class SystemPage(BaseSettingsPage):
    def __init__(self, main_window, **kwargs):
        super().__init__(main_window, **kwargs)

        content = self.create_scrolled_content()

        ## GROUP: System ##
        group = self.create_group(
            _("System"),
            _("General system settings."),
            "system"
        )
        content.append(group)

        # sshEnable
        self.create_row(group,
            _("SSH always on"),
            _("Turn on ssh remote access at boot."),
            "sshEnable",
            "ssh-symbolic"
        )

        # fastGrub
        self.create_row(
            group,
            _("Fast Grub"),
            _("Decreases grub display time."),
            "fastGrub",
            "grub-symbolic"
        )

        # bigMount
        self.create_row(
            group,
            _("Auto-mount Partitions"),
            _("Auto mount partitions in internal disks on boot."),
            "bigMount",
            "bigmount-symbolic"
        )

        # Meltdown mitigations
        link_meltdown = "https://meltdownattack.com"
        self.create_row(
            group,
            _("Meltdown Mitigations off"),
            _("Using mitigations=off will make your machine faster and less secure! For more information see: <a href='{l}'>{l}</a>").format(l=link_meltdown),
            "meltdownMitigations",
            "meltdown-mitigations-symbolic"
        )

        # noWatchdog
        self.create_row(
            group,
            _("noWatchdog"),
            _("Disables the hardware watchdog and TSC clocksource systems, maintaining high performance but removing automatic protections against system crashes."),
            "noWatchdog",
            "watchdog-symbolic"
        )

        # # Limits
        # self.create_row(
        #     group,
        #     _("Memlock and rtprio"),
        #     _("Set memlock to unlimited and rtprio to 90."),
        #     "limits",
        #     "limits-symbolic",
        # )

        self.sync_all_switches()
