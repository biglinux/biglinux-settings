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

class PerformanceGamesPage(BaseSettingsPage):
    def __init__(self, main_window, **kwargs):
        super().__init__(main_window, **kwargs)

        # Create the container (base method)
        content = self.create_scrolled_content()

        ## GROUP ##

        # Performance
        performance_group = self.create_group(
            _("Performance"),
            _("Ajustes de Performance do BigLinux."),
            "perf_games"
        )
        content.append(performance_group)

        # Games
        games_group = self.create_group(
            _("Games Booster"),
            _("Combination of daemon and library that allows games to request a set of optimizations be temporarily applied to the operating system and/or the game process."),
            "perf_games"
        )
        content.append(games_group)


        ## Performance ##
        # Disable Visual Effects
        self.create_row(
            performance_group,
            _("Disable Visual Effects"),
            _("Desativa efeitos visuais do KWin (blur, sombras, animações). Diminui carga na GPU e libera memória."),
            "disableVisualEffects",
            "disable-visual-effects-symbolic"
        )
        # Compositor Settings
        self.create_row(
            performance_group,
            _("Compositor Settings"),
            _("Configura compositor para “low latency”, permite tearing e desativa animações. Minimiza a sobrecarga de composição e reduz input lag."),
            "compositorSettings",
            "compositor-settings-symbolic"
        )
        # CPU Maximum Performance
        self.create_row(
            performance_group,
            _("CPU Maximum Performance"),
            _("Força o modo máximo de desempenho do processador. Garante que o processador use a frequência máxima."),
            "cpuMaximumPerformance",
            "cpu-maximum-performance-symbolic"
        )
        # GPU Maximum Performance
        self.create_row(
            performance_group,
            _("GPU Maximum Performance"),
            _("Força o modo máximo de desempenho (GPU NVIDIA/AMD). Garante que a placa de vídeo use a frequência máxima."),
            "gpuMaximumPerformance",
            "gpu-maximum-performance-symbolic"
        )
        # Disable Baloo Indexer
        self.create_row(
            performance_group,
            _("Disable Baloo Indexer"),
            _("Desativa o indexador de arquivos Baloo. Evita I/O de disco."),
            "disableBalooIndexer",
            "disable-baloo-indexer-symbolic"
        )
        # Stop Akonadi Server
        self.create_row(
            performance_group,
            _("Stop Akonadi Server"),
            _("Interrompe o servidor de dados de PIM (Kontact/Thunderbird). Reduz a sobrecarga de memória e disco."),
            "stopAkonadiServer",
            "stop-akonadi-server-symbolic"
        )
        # Unload S.M.A.R.T Monitor
        self.create_row(
            performance_group,
            _("Unload S.M.A.R.T Monitor"),
            _("Desativa monitoramento S.M.A.R.T. de discos. Reduz I/O de disco e CPU."),
            "unloadSmartMonitor",
            "unload-smart-monitor-symbolic"
        )


        ## GAMES ##
        # Game Mode Daemon
        self.create_row(
            games_group,
            _("GameMode Daemon"),
            _("Ativa o daemon que ajusta CPU, I/O, etc. Reduz a latência e aumenta a taxa de quadros."),
            "gamemodeDaemon",
            "gamemode-daemon-symbolic"
        )

        self.sync_all_switches()
