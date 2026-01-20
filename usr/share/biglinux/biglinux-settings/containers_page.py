
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
