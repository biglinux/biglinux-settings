from base_page import BaseSettingsPage, _


class PerformancePage(BaseSettingsPage):
    def __init__(self, main_window, **kwargs):
        super().__init__(main_window, **kwargs)

        # Create the container (base method)
        content = self.create_scrolled_content()

        ## GROUP ##

        # Performance
        performance_group = self.create_group(
            _("Performance"),
            _("BigLinux performance tweaks."),
            "performance"
        )
        content.append(performance_group)

        # # Games
        # games_group = self.create_group(
        #     _("Games Booster"),
        #     _("Combination of daemon and library that allows games to request a set of optimizations be temporarily applied to the operating system and/or the game process."),
        #     "perf_games"
        # )
        # content.append(games_group)


        ## Performance ##
        # Disable Visual Effects
        self.create_row(
            performance_group,
            _("Disable Visual Effects"),
            _("Disables KWin visual effects (blur, shadows, animations). Reduces GPU load and frees memory."),
            "disableVisualEffects",
            "disable-visual-effects-symbolic"
        )
        # Compositor Settings
        self.create_row(
            performance_group,
            _("Compositor Settings"),
            _("Configures compositor for low latency, allows tearing and disables animations. Minimizes compositing overhead and reduces input lag."),
            "compositorSettings",
            "compositor-settings-symbolic"
        )
        # CPU Maximum Performance
        self.create_row(
            performance_group,
            _("CPU Maximum Performance"),
            _("Forces maximum processor performance mode. Ensures the processor uses maximum frequency."),
            "cpuMaximumPerformance",
            "cpu-maximum-performance-symbolic"
        )
        # GPU Maximum Performance
        self.create_row(
            performance_group,
            _("GPU Maximum Performance"),
            _("Forces maximum GPU performance mode (NVIDIA/AMD). Ensures the graphics card uses maximum frequency."),
            "gpuMaximumPerformance",
            "gpu-maximum-performance-symbolic"
        )
        # Disable Baloo Indexer
        self.create_row(
            performance_group,
            _("Disable Baloo Indexer"),
            _("Disables the Baloo file indexer. Avoids disk I/O overhead."),
            "disableBalooIndexer",
            "disable-baloo-indexer-symbolic"
        )
        # Stop Akonadi Server
        self.create_row(
            performance_group,
            _("Stop Akonadi Server"),
            _("Stops the PIM data server (Kontact/Thunderbird). Reduces memory and disk overhead."),
            "stopAkonadiServer",
            "stop-akonadi-server-symbolic"
        )
        # Unload S.M.A.R.T Monitor
        self.create_row(
            performance_group,
            _("Unload S.M.A.R.T Monitor"),
            _("Disables S.M.A.R.T disk monitoring. Reduces disk I/O and CPU usage."),
            "unloadSmartMonitor",
            "unload-smart-monitor-symbolic"
        )



        # ## GAMES ##
        # # Game Mode Daemon
        # gameMode = self.create_row(
        #     games_group,
        #     _("GameMode Daemon"),
        #     _("Activates daemon that adjusts CPU, I/O, etc. Reduces latency and increases frame rate."),
        #     "gamemodeDaemon",
        #     "gamemode-daemon-symbolic"
        # )
        # # self.create_sub_row(
        # #     games_group,
        # #     _("Sub‑Feature B"),
        # #     _("Option B for the main feature."),
        # #     "gamemodeDaemon",
        # #     "gamemode-daemon-symbolic",
        # #     gameMode
        # # )

        self.sync_all_switches()
