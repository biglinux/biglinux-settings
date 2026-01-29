from base_page import BaseSettingsPage, _


class UsabilityPage(BaseSettingsPage):
    def __init__(self, main_window, **kwargs):
        super().__init__(main_window, **kwargs)

        content = self.create_scrolled_content()

        ## GROUP: Usability ##
        group = self.create_group(
            _("Usability"),
            _("User and Visual system settings."),
            "usability"
        )
        content.append(group)

        # numLock
        self.create_row(
            group,
            _("NumLock"),
            _("Initial NumLock state. Ignored if autologin is enabled."),
            "numLock",
            "numlock-symbolic"
        )

        # windowButtonOnLeftSide
        self.create_row(
            group,
            _("Window Button On Left Side"),
            _("Maximize, minimize, and close buttons on the left side of the window."),
            "windowButtonOnLeftSide",
            "window-controls-symbolic"
        )

        # sshStart
        self.create_row(
            group,
            _("SSH until next reboot"),
            _("Enable remote access via ssh until next boot."),
            "sshStart",
            "ssh-symbolic"
        )

        # KZones
        self.create_row(
            group,
            _("KZones"),
            _("Script for the KWin window manager of the KDE Plasma desktop environment."),
            "kzones",
            "kzones-symbolic"
        )

        # Recent Files & Locations
        self.create_row(
            group,
            _("Recent Files & Locations"),
            _("Restores the 'Recent Files' and 'Recent Locations' functionality that appears empty in Dolphin and the Application Menu."),
            "recentFiles",
            "recent_files-symbolic"
        )

        self.sync_all_switches()
