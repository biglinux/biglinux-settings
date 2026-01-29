import os
import subprocess
from base_page import BaseSettingsPage, _

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
            _("Containers"),
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

    def install_container(self, container_name):
        """Install a Docker container."""
        script_path = os.path.join("containers", f"{container_name}.sh")
        if not os.path.exists(script_path):
            print(f"Error: Script not found for {container_name}")
            return False

        try:
            result = subprocess.run(
                [script_path, "install"], capture_output=True, text=True
            )
            if result.returncode == 0:
                print(f"{container_name} installed successfully")
                # Reload the page after successful installation
                self.sync_all_switches()
                return True
            else:
                print(f"Failed to install {container_name}: {result.stderr}")
                return False
        except Exception as e:
            print(f"Error during installation: {e}")
            return False

    def remove_container(self, container_name):
        """Remove a Docker container."""
        script_path = os.path.join("containers", f"{container_name}.sh")
        if not os.path.exists(script_path):
            print(f"Error: Script not found for {container_name}")
            return False

        try:
            result = subprocess.run(
                [script_path, "remove"], capture_output=True, text=True
            )
            if result.returncode == 0:
                print(f"{container_name} removed successfully")
                # Reload the page after successful removal
                self.sync_all_switches()
                return True
            else:
                print(f"Failed to remove {container_name}: {result.stderr}")
                return False
        except Exception as e:
            print(f"Error during removal: {e}")
            return False

    def _run_script_no_timeout(self, script_path, state):
        """
        Execute the toggle command for a script without a hard timeout.
        Returns True if the script reports success (return code 0), False otherwise.
        """
        state_str = "true" if state else "false"
        try:
            result = subprocess.run(
                [script_path, "toggle", state_str],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return True
            else:
                print(f"Script {os.path.basename(script_path)} returned error {result.returncode}")
                print(f"stderr: {result.stderr}")
                return False
        except Exception as e:
            print(f"Error running script {os.path.basename(script_path)}: {e}")
            return False

    def on_switch_changed(self, switch, state):
        """Callback executed when a user manually toggles a switch."""
        script_path = self.switch_scripts.get(switch)

        if script_path:
            script_name = os.path.basename(script_path)
            print(_("Changing {} to {}").format(script_name, "on" if state else "off"))

            # Execute the script without a timeout
            success = self._run_script_no_timeout(script_path, state)

            # If the script fails, revert the switch to its previous state
            if not success:
                # Block signal to prevent an infinite loop
                switch.handler_block_by_func(self.on_switch_changed)
                switch.set_active(not state)
                switch.handler_unblock_by_func(self.on_switch_changed)

                print(
                    _("ERROR: Failed to change {} to {}").format(
                        script_name, "on" if state else "off"
                    )
                )
                self.main_window.show_toast(_("Failed to change setting: {}").format(script_name))
            else:
                # After a successful change, refresh all switches to reflect real state
                self.sync_all_switches()

        return False