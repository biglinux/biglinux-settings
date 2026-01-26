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

class DockerPage(BaseSettingsPage):
    def __init__(self, main_window, **kwargs):
        super().__init__(main_window, **kwargs)

        # Create the container (base method)
        content = self.create_scrolled_content()

        # Create the group (base method)
        docker_group = self.create_group(
            _("Docker"),
            _("Container service - enable to use containers below."),
            "docker"
        )
        content.append(docker_group)

        # Create the group (base method)
        container_group = self.create_group(
            _("Docker"),
            _("Manage container technologies."),
            "docker"
        )
        content.append(container_group)

        ## Docker
        # Docker
        self.create_row(
            docker_group,
            _("Docker"),
            _("Docker Enabled."),
            "dockerEnable",
            "docker-symbolic"
        )


        ## Container
        # BigLinux Docker Nextcloud Plus
        self.create_row(
            container_group,
            _("Nextcloud Plus"),
            _("Nextcloud Plus container."),
            "nextcloud-plus",
            "docker-nextcloud-plus-symbolic"
        )
        # BigLinux Docker AdGuard
        self.create_row(
            container_group,
            _("AdGuard"),
            _("AdGuard Home container."),
            "adguard",
            "docker-adguard-symbolic"
        )
        # BigLinux Docker Django
        self.create_row(
            container_group,
            _("Django"),
            _("Django developer environment."),
            "django",
            "docker-django-symbolic"
        )
        # BigLinux Docker Duplicati
        self.create_row(
            container_group,
            _("Duplicati"),
            _("Duplicati backup solution."),
            "duplicati",
            "docker-duplicati-symbolic"
        )
        # BigLinux Docker Jellyfin
        self.create_row(
            container_group,
            _("Jellyfin"),
            _("Jellyfin media server."),
            "jellyfin",
            "docker-jellyfin-symbolic"
        )
        # BigLinux Docker LAMP
        self.create_row(
            container_group,
            _("LAMP"),
            _("LAMP stack (Linux, Apache, MySQL, PHP)."),
            "lamp",
            "docker-lamp-symbolic"
        )
        # BigLinux Docker Portainer Client
        self.create_row(
            container_group,
            _("Portainer Client"),
            _("Portainer Agent for cluster management."),
            "portainer-client",
            "docker-portainer-client-symbolic"
        )
        # BigLinux Docker SWS
        self.create_row(
            container_group,
            _("SWS"),
            _("SWS static web server."),
            "sws",
            "docker-sws-symbolic"
        )
        # BigLinux Docker V2RayA
        self.create_row(
            container_group,
            _("V2RayA"),
            _("V2RayA network tool."),
            "v2raya",
            "docker-v2raya-symbolic"
        )

        # Syncs
        self.sync_all_switches()
