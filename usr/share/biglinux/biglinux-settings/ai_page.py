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

class AIPage(BaseSettingsPage):
    def __init__(self, main_window, **kwargs):
        super().__init__(main_window, **kwargs)

        # Create the container (base method)
        content = self.create_scrolled_content()

        # Create the group (base method)
        group = self.create_group(
            _("Artificial Intelligence"),
            _("AI settings and tools."),
            "ai"
        )
        content.append(group)

        # Generative AI for Krita
        self.create_row(
            group,
            _("Generative AI for Krita"),
            _("This is a plugin to use generative AI in painting and image editing workflows directly in Krita."),
            "krita",
            "krita-ai-symbolic",
        )
        # ChatAI
        self.create_row(
            group,
            _("ChatAI"),
            _("A variety of chats like Plasmoid for your KDE Plasma desktop."),
            "chatai",
            "chatai-symbolic",
        )

        # Syncs
        self.sync_all_switches()
