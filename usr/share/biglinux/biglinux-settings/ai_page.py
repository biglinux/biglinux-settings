from base_page import BaseSettingsPage, _


class AIPage(BaseSettingsPage):
    def __init__(self, main_window, **kwargs):
        super().__init__(main_window, **kwargs)

        local_ip = self.get_local_ip()

        # Create the container (base method)
        content = self.create_scrolled_content()

        # # Create the group (base method)
        # group = self.create_group(
        #     _("Artificial Intelligence"), _("AI settings and tools."), "ai"
        # )
        # content.append(group)

        # Create the group Ollama (base method)
        aiGui = self.create_group(
            _("AI Interfaces"),
            _("Graphical interface for artificial intelligence.."),
            "ai",
        )
        content.append(aiGui)

        # Create the group Ollama (base method)
        ollamaServer = self.create_group(
            _("Ollma Server"),
            _("Choose which Ollama server is best for your hardware."),
            "ai",
        )
        content.append(ollamaServer)

        # Generative AI for Krita
        # self.create_row(
        #     group,
        #     _("Generative AI for Krita"),
        #     _("This is a plugin to use generative AI in painting and image editing workflows directly in Krita."),
        #     "krita",
        #     "krita-ai-symbolic",
        #     info_text=_("Open Krita, open an existing drawing or create a new one.\nIn the top panel go to Settings > Panels > check the AI Image Generation box.\n\nIn the window that opens on the bottom right.\nClick Configure > Local Managed Server, choose your GPU or CPU, choose the model in Workloads and click Install."),
        # )
        # ChatAI
        self.create_row(
            aiGui,
            _("ChatAI"),
            _("A variety of chats like Plasmoid for your KDE Plasma desktop."),
            "chatai",
            "chatai-symbolic",
        )
        # Ollama LAB
        self.create_row(
            aiGui,
            _("Ollama LAB"),
            _("Graphical interface for managing Ollama models and chat."),
            "ollamaLab",
            "ollama-symbolic",
        )
        # ChatBox
        self.create_row(
            aiGui,
            ("ChatBox"),
            _("User-friendly Desktop Client App for AI Models/LLMs."),
            "chatbox",
            "chatbox-symbolic",
        )
        # LM Studio
        self.create_row(
            aiGui,
            _("LM Studio"),
            _("LM Studio - A desktop app for exploring and running large language models locally."),
            "lmStudio",
            "lmstudio-symbolic",
        )
        # Open Notebook
        self.create_row(
            aiGui,
            ("Open Notebook"),
            _("An open source, privacy-focused alternative to Google's Notebook LM!"),
            "openNotebookInstall",
            "openNotebook-symbolic",
        )
        # ComfyUI
        comfyUI = self.create_row(
            aiGui,
            _("ComfyUI (GPU ONLY)"),
            _("The most powerful and modular visual AI engine and application."),
            "comfyUI",
            "comfyUI-symbolic",
            timeout=1200,
        )
        self.create_sub_row(
            aiGui,
            _("ComfyUI Server"),
            _("start ComfyUI Server."),
            "comfyUIRun",
            "comfyUI-symbolic",
            comfyUI,
            info_text=_("ComfyUI server is running.\nAddress: http://localhost:8188\nand\nAddress: http://{}:8188").format(local_ip),
        )
        # Ollama CPU
        ollama = self.create_row(
            ollamaServer,
            _("OllamaCPU"),
            _("Local AI server. For CPUs only."),
            "ollamaCpu",
            "ollama-symbolic",
            info_text=_("Ollama server is running.\nAddress: http://localhost:11434"),
        )
        self.create_sub_row(
            ollamaServer,
            _("Share Ollama"),
            _("Share ollama on the local network."),
            "ollamaShare",
            "ollama-symbolic",
            ollama,
            info_text=_("Ollama server is running.\nAddress: http://{}:11434").format(
                local_ip
            ),
        )
        # Ollama Vulkan
        ollama = self.create_row(
            ollamaServer,
            _("Ollama Vulkan"),
            _("Local AI server. For CPUs, AMD/Nvidia and integrated GPUs."),
            "ollamaVulkan",
            "ollama-symbolic",
            info_text=_("Ollama server is running.\nAddress: http://localhost:11434"),
        )
        self.create_sub_row(
            ollamaServer,
            _("Share Ollama"),
            _("Share ollama on the local network."),
            "ollamaShare",
            "ollama-symbolic",
            ollama,
            info_text=_("Ollama server is running.\nAddress: http://{}:11434").format(
                local_ip
            ),
        )
        # Ollama Nvidia CUDA
        ollama = self.create_row(
            ollamaServer,
            _("Ollama Nvidia CUDA"),
            _("Local AI server. For newer Nvidia GPUs, starting from the 2000 series."),
            "ollamaNvidia",
            "ollama-symbolic",
            info_text=_("Ollama server is running.\nAddress: http://localhost:11434"),
        )
        self.create_sub_row(
            ollamaServer,
            _("Share Ollama"),
            _("Share ollama on the local network."),
            "ollamaShare",
            "ollama-symbolic",
            ollama,
            info_text=_("Ollama server is running.\nAddress: http://{}:11434").format(
                local_ip
            ),
        )
        # Ollama AMD ROCm
        ollama = self.create_row(
            ollamaServer,
            _("Ollama AMD ROCm"),
            _(
                "Local AI server. For newer AMD GPUs, starting from the 6000 series.\nConsider using Vulkan, in many tests, Vulkan performed better than ROCm."
            ),
            "ollamaAmd",
            "ollama-symbolic",
            info_text=_("Ollama server is running.\nAddress: http://localhost:11434"),
        )
        self.create_sub_row(
            ollamaServer,
            _("Share Ollama"),
            _("Share ollama on the local network."),
            "ollamaShare",
            "ollama-symbolic",
            ollama,
            info_text=_("Ollama server is running.\nAddress: http://{}:11434").format(
                local_ip
            ),
        )

        # Syncs
        self.sync_all_switches()
