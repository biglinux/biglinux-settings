
from gi.repository import Gtk, Adw
from base_page import BaseSettingsPage
import gettext

DOMAIN = 'biglinux-settings'
LOCALE_DIR = '/usr/share/locale'
gettext.bindtextdomain(DOMAIN, LOCALE_DIR)
gettext.textdomain(DOMAIN)
_ = gettext.gettext

class ContainersPage(BaseSettingsPage):
    def populate_content(self, content_box):
        self.containers_group(content_box)

    def containers_group(self, parent):
        group = Adw.PreferencesGroup()
        group.set_title(_("Containers"))
        group.script_group = "system" # Docker script is in 'system'
        group.set_description(_("Manage container technologies"))
        parent.append(group)

        # Docker
        self.Docker_switch = self.create_row_with_clickable_link(
            group,
            _("Docker"),
            _("Docker Enabled."),
            "dockerEnable",
            icon_name="docker"
        )

        # BigLinux Docker Nextcloud Plus
        self.create_row_with_clickable_link(
            group,
            _("Nextcloud Plus"),
            _("Nextcloud Plus container."),
            "biglinux-docker-nextcloud-plus",
            icon_name="nextcloud"
        )

        # BigLinux Docker AdGuard
        self.create_row_with_clickable_link(
            group,
            _("AdGuard"),
            _("AdGuard Home container."),
            "biglinux-docker-adguard",
            icon_name="adguard-home"
        )

        # BigLinux Docker Django
        self.create_row_with_clickable_link(
            group,
            _("Django"),
            _("Django developer environment."),
            "biglinux-docker-django",
            icon_name="python"
        )

        # BigLinux Docker Duplicati
        self.create_row_with_clickable_link(
            group,
            _("Duplicati"),
            _("Duplicati backup solution."),
            "biglinux-docker-duplicati",
            icon_name="duplicati"
        )

        # BigLinux Docker Jellyfin
        self.create_row_with_clickable_link(
            group,
            _("Jellyfin"),
            _("Jellyfin media server."),
            "biglinux-docker-jellyfin",
            icon_name="jellyfin"
        )

        # BigLinux Docker LAMP
        self.create_row_with_clickable_link(
            group,
            _("LAMP"),
            _("LAMP stack (Linux, Apache, MySQL, PHP)."),
            "biglinux-docker-lamp",
            icon_name="server-database"
        )

        # BigLinux Docker Portainer Client
        self.create_row_with_clickable_link(
            group,
            _("Portainer Client"),
            _("Portainer Agent for cluster management."),
            "biglinux-docker-portainer-client",
            icon_name="portainer"
        )

        # BigLinux Docker SWS
        self.create_row_with_clickable_link(
            group,
            _("SWS"),
            _("SWS static web server."),
            "biglinux-docker-sws",
            icon_name="www"
        )

        # BigLinux Docker V2RayA
        self.create_row_with_clickable_link(
            group,
            _("V2RayA"),
            _("V2RayA network tool."),
            "biglinux-docker-v2raya",
            icon_name="v2raya"
        )
