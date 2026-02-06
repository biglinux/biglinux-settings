from base_page import BaseSettingsPage, _


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
        ssh = self.create_row(
            group,
            _("SSH"),
            _("Enable remote access via ssh."),
            "sshStart",
            "ssh-symbolic",
        )
        self.create_sub_row(
            group,
            _("SSH always on"),
            _("Turn on ssh remote access at boot."),
            "sshEnable",
            "ssh-symbolic",
            ssh,
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

        # # Limits
        # self.create_row(
        #     group,
        #     _("Memlock and rtprio"),
        #     _("Set memlock to unlimited and rtprio to 90."),
        #     "limits",
        #     "limits-symbolic",
        # )

        self.sync_all_switches()
