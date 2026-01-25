from base_page import BaseSettingsPage
import gettext
_ = gettext.gettext

class SystemUsabilityPage(BaseSettingsPage):
    def __init__(self, main_window, **kwargs):
        super().__init__(main_window, **kwargs)

        content = self.create_scrolled_content()

        ## GROUP: Usability ##
        usability_group = self.create_group(
            _("Usability"),
            _("User and Visual system settings."),
            "usability"
        )
        content.append(usability_group)

        # numLock
        self.create_row(
            usability_group,
            _("NumLock"),
            _("Initial NumLock state. Ignored if autologin is enabled."),
            "numLock",
            "numlock-symbolic"
        )

        # windowButtonOnLeftSide
        self.create_row(
            usability_group,
            _("Window Button..."),
            _("Maximize, minimize, and close buttons on the left side of the window."),
            "windowButtonOnLeftSide",
            "window-controls-symbolic"
        )

        # sshStart
        self.create_row(
            usability_group,
            _("SSH until next reboot"),
            _("Enable remote access via ssh until next boot."),
            "sshStart",
            "ssh-symbolic"
        )

        # KZones
        self.create_row(
            usability_group,
            _("KZones"),
            _("Script for the KWin window manager of the KDE Plasma desktop environment."),
            "kzones",
            "kzones-symbolic"
        )

        # Game Mode Booster
        self.create_row(
            usability_group,
            _("Game Mode Booster"),
            _("Combination of daemon and library that allows games to request a set of optimizations be temporarily applied to the operating system and/or the game process."),
            "gamemode",
            "gamemode-symbolic"
        )

        # Recent Files & Locations
        self.create_row(
            usability_group,
            _("Recent Files & Locations"),
            _("Restores the 'Recent Files' and 'Recent Locations' functionality that appears empty in Dolphin and the Application Menu."),
            "recent_files",
            "recent_files-symbolic"
        )


        ## GROUP: System ##
        system_group = self.create_group(
            _("System"),
            _("General system settings"),
            "system"
        )
        content.append(system_group)

        # sshEnable
        self.create_row(system_group,
            _("SSH always on"),
            _("Turn on ssh remote access at boot."),
            "sshEnable",
            "ssh-symbolic"
        )

        # fastGrub
        self.create_row(
            system_group,
            _("Fast Grub"),
            _("Decreases grub display time."),
            "fastGrub",
            "grub-symbolic"
        )

        # bigMount
        self.create_row(
            system_group,
            _("Auto-mount Partitions"),
            _("Auto mount partitions in internal disks on boot."),
            "bigMount",
            "bigmount-symbolic"
        )

        # Meltdown mitigations
        link_meltdown = "https://meltdownattack.com"
        self.create_row(
            system_group,
            _("Meltdown Mitigations off"),
            _("Using mitigations=off will make your machine faster and less secure! For more information see: <a href='{l}'>{l}</a>").format(l=link_meltdown),
            "meltdownMitigations",
            "meltdown-mitigations-symbolic"
        )

        # noWatchdog
        self.create_row(
            system_group,
            _("noWatchdog"),
            _("Disables the hardware watchdog and TSC clocksource systems, maintaining high performance but removing automatic protections against system crashes."),
            "noWatchdog",
            "watchdog-symbolic"
        )

        # # Limits
        # self.create_row(
        #     system_group,
        #     _("Memlock and rtprio"),
        #     _("Set memlock to unlimited and rtprio to 90."),
        #     "limits",
        #     "limits-symbolic",
        # )

        self.sync_all_switches()
