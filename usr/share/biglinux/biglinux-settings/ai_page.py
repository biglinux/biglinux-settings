from base_page import BaseSettingsPage
import gettext
_ = gettext.gettext

class AIPage(BaseSettingsPage):
    def __init__(self, main_window, **kwargs):
        super().__init__(main_window, **kwargs)

        # Create the container (base method)
        content = self.create_scrolled_content()

        # Create the group (base method)
        group = self.create_group(
            _("Artificial Intelligence"),
            _("AI settings and tools."),
            "docker"
        )
        content.append(group)

        # numLock
        self.create_row(
            group,
            _("NumLock"),
            _("Initial NumLock state. Ignored if autologin is enabled."),
            "numLock",
            "numlock-symbolic",
        )
        # KZones
        self.create_row(
            group,
            _("KZones"),
            _("Script for the KWin window manager of the KDE Plasma desktop environment."),
            "kzones",
            "kzones-symbolic",
        )

        # Syncs
        self.sync_all_switches()
