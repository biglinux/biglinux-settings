#!/usr/bin/env python3
import os
import subprocess
import shutil
import sys
import time

# --- Configurações e Cores ---
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

# Lista de efeitos pesados para desativar no Plasma 6
EFFECTS_TO_DISABLE = [
    "blur",
    "contrast",
    "kwin4_effect_translucency",  # Transparência
    "kwin4_effect_diminactive",   # Escurecer janelas inativas
    "kwin4_effect_fade",          # Fade in/out
    "kwin4_effect_dialogparent",  # Escurecer fundo de diálogos
    "slidingpopups",              # Menus deslizando
    "kwin4_effect_login",
    "kwin4_effect_windowaperture"
]

# Caminhos de configuração
HOME = os.path.expanduser("~")
KWINRC = os.path.join(HOME, ".config", "kwinrc")
KDEGLOBALS = os.path.join(HOME, ".config", "kdeglobals")

def run_cmd(command):
    """Executa um comando shell e suprime a saída, a menos que haja erro."""
    try:
        subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def check_plasma_version():
    """Verifica se as ferramentas do Plasma 6 estão disponíveis."""
    if shutil.which("kwriteconfig6"):
        return "kwriteconfig6", "balooctl6"
    elif shutil.which("kwriteconfig5"):
        # print(f"{Colors.YELLOW}Aviso: Plasma 6 não detectado, tentando ferramentas do Plasma 5...{Colors.RESET}")
        return "kwriteconfig5", "balooctl"
    else:
        # print(f"{Colors.RED}Erro: Ferramentas de configuração do KDE não encontradas.{Colors.RESET}")
        return None, None

KWRITE_CMD, BALOO_CMD = check_plasma_version()

def backup_config():
    """Faz backup do kwinrc antes de modificar."""
    backup_path = f"{KWINRC}.backup_booster"
    if not os.path.exists(backup_path):
        # print(f"Criando backup em: {Colors.YELLOW}{backup_path}{Colors.RESET}")
        shutil.copy2(KWINRC, backup_path)
    else:
        pass
        # print("Backup já existe, ignorando criação.")

def set_config(file, group, key, value, delete=False):
    """Wrapper para o kwriteconfig."""
    if not KWRITE_CMD:
        return
    cmd = f"{KWRITE_CMD} --file {file} --group {group} --key {key}"
    if delete:
        run_cmd(f"{cmd} --delete")
    else:
        run_cmd(f"{cmd} {value}")

def reload_kwin():
    """Recarrega o KWin para aplicar as mudanças."""
    # print("Recarregando KWin...")
    # Tenta o método DBus padrão do Plasma 6
    methods = [
        "dbus-send --session --dest=org.kde.KWin /KWin org.kde.KWin.reconfigure",
        "qdbus6 org.kde.KWin /KWin reconfigure",
        "qdbus org.kde.KWin /KWin reconfigure"
    ]
    
    success = False
    for method in methods:
        if run_cmd(method):
            success = True
            break
    
    # if not success:
    #     print(f"{Colors.RED}Aviso: Não foi possível recarregar o KWin automaticamente via DBus.{Colors.RESET}")

def enable_booster():
    # print(f"{Colors.GREEN}>>> ATIVANDO MODO BOOSTER (PERFORMANCE){Colors.RESET}")
    backup_config()

    # 1. Desativar Efeitos (Plugins)
    # print("Desativando efeitos visuais (Blur, Transparência, Sombras)...")
    for effect in EFFECTS_TO_DISABLE:
        set_config("kwinrc", "Plugins", f"{effect}Enabled", "false")

    # 2. Ajustes de Latência e Renderização
    # print("Otimizando latência...")
    set_config("kwinrc", "Compositing", "LatencyPolicy", "Low")
    set_config("kwinrc", "Compositing", "RenderTimeEstimator", "false")
    # Tenta desativar VSync (pode causar tearing, mas aumenta FPS)
    set_config("kwinrc", "Compositing", "WindowsBlockCompositing", "true")

    # 3. Remover Animações
    # print("Removendo animações globais...")
    set_config("kdeglobals", "KDE", "AnimationDurationFactor", "0")

    # 4. Parar Baloo (Indexador)
    if BALOO_CMD:
        # print("Parando indexador de arquivos (Baloo)...")
        run_cmd(f"{BALOO_CMD} suspend")
        run_cmd(f"{BALOO_CMD} disable")

    reload_kwin()
    # print(f"{Colors.GREEN}>>> CONCLUÍDO! O sistema está otimizado.{Colors.RESET}")

def disable_booster():
    # print(f"{Colors.YELLOW}>>> RESTAURANDO CONFIGURAÇÕES PADRÃO{Colors.RESET}")

    # 1. Reativar Efeitos
    # print("Reativando efeitos visuais...")
    for effect in EFFECTS_TO_DISABLE:
        set_config("kwinrc", "Plugins", f"{effect}Enabled", "true")

    # 2. Restaurar Latência
    # print("Restaurando latência padrão...")
    set_config("kwinrc", "Compositing", "LatencyPolicy", "", delete=True)
    set_config("kwinrc", "Compositing", "RenderTimeEstimator", "true")

    # 3. Restaurar Animações
    # print("Restaurando animações...")
    set_config("kdeglobals", "KDE", "AnimationDurationFactor", "1")

    # 4. Reativar Baloo
    if BALOO_CMD:
        # print("Reativando Baloo...")
        run_cmd(f"{BALOO_CMD} enable")
        run_cmd(f"{BALOO_CMD} resume")

    reload_kwin()
    # print(f"{Colors.GREEN}>>> CONCLUÍDO! O sistema voltou ao normal.{Colors.RESET}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # print(f"Uso: python3 kde_booster.py {Colors.GREEN}[on|off]{Colors.RESET}")
        sys.exit(1)

    action = sys.argv[1].lower()
    
    if action == "on":
        enable_booster()
    elif action == "off":
        disable_booster()
    else:
        pass
        # print("Opção inválida. Use 'on' ou 'off'.")
