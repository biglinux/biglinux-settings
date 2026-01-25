from base_page import BaseSettingsPage
import gettext
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

        # Syncs
        self.sync_all_switches()
