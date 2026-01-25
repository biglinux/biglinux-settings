from base_page import BaseSettingsPage
import gettext
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
        #

        # Syncs
        self.sync_all_switches()
