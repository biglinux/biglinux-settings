#!/bin/bash

# Function to detect GPU
get_gpu() {
    if lspci | grep -i nvidia > /dev/null; then
        echo "NVIDIA"
    elif lspci | grep -i "radeon\|amd" > /dev/null; then
        echo "AMD"
    elif lspci | grep -i intel > /dev/null; then
        echo "Intel"
    else
        echo "Software"
    fi
}

check() {
    if [ -f "$HOME/.local/share/krita/pykrita/ai_diffusion.ini" ]; then
        echo "true"
    else
        echo "false"
    fi
}

install_gui() {
    GPU_TYPE=$1
    RENDER_MODE=$2
    
    echo "STATUS: Preparando instalação..."
    echo "PROGRESS: 10"
    
    # Check Krita
    INSTALLED_NATIVE=false
    INSTALLED_FLATPAK=false
    
    if pacman -Q krita &>/dev/null; then
        INSTALLED_NATIVE=true
        echo "Krita nativo detectado."
    elif flatpak list | grep -q "org.kde.krita"; then
        INSTALLED_FLATPAK=true
        echo "Krita Flatpak detectado."
    fi
    
    if [ "$INSTALLED_NATIVE" = false ] && [ "$INSTALLED_FLATPAK" = false ]; then
        echo "STATUS: Instalando Krita (Nativo)..."
        echo "Solicitando permissão para instalar Krita..."
        # User requested: sudo pacman -Sy krita
        if ! pkexec pacman -Sy --noconfirm krita; then
            echo "Erro: Falha ao instalar Krita"
            exit 1
        fi
    fi
    echo "PROGRESS: 40"

    # Backend
    echo "STATUS: Configurando Backend GPU ($GPU_TYPE)..."
    SKIP_TORCH_PIP=false
    PYTORCH_DEPS="torch torchvision" # Default for software

    case $GPU_TYPE in
        "NVIDIA")
            # Try to install system packages for NVIDIA
            if pkexec pacman -S --noconfirm python-pytorch-cuda python-torchvision cuda cudnn python-torch-opt-cuda; then
                echo "Pacotes de sistema (NVIDIA) instalados."
                SKIP_TORCH_PIP=true
            else
                echo "Falha na instalação via pacman (NVIDIA). Tentando via PIP..."
                PYTORCH_DEPS="torch torchvision --index-url https://download.pytorch.org/whl/cu118"
            fi
            ;;
        "AMD")
            # Try to install system packages for AMD
            if pkexec pacman -S --noconfirm python-pytorch-rocm python-torchvision rocm-hip-sdk; then
                 echo "Pacotes de sistema (AMD) instalados."
                 SKIP_TORCH_PIP=true
            else
                 echo "Falha na instalação via pacman (AMD). Tentando via PIP..."
                 PYTORCH_DEPS="torch torchvision --index-url https://download.pytorch.org/whl/rocm5.6"
            fi
            ;;
        *)
            # Software mode
            ;;
    esac
    echo "PROGRESS: 60"
    
    # Plugin Installation (Manual Method - More Stable than AUR)
    echo "STATUS: Instalando Plugin (GitHub)..."
    
    # Get dynamic URL for latest release
    API_URL="https://api.github.com/repos/Acly/krita-ai-diffusion/releases/latest"
    PLUGIN_URL=$(curl -s "$API_URL" | grep "browser_download_url" | grep ".zip" | head -n 1 | cut -d '"' -f 4)
    
    if [ -z "$PLUGIN_URL" ]; then
        PLUGIN_URL="https://github.com/Acly/krita-ai-diffusion/releases/latest/download/krita_ai_diffusion.zip"
    fi

    echo "Baixando: $PLUGIN_URL"
    TEMP_ZIP="/tmp/krita_ai_diffusion.zip"
    
    if ! curl -L -f -o "$TEMP_ZIP" "$PLUGIN_URL"; then
        echo "Erro ao baixar plugin."
        exit 1
    fi
    
    # Ensure directory exists
    PYKRITA_DIR="$HOME/.local/share/krita/pykrita"
    mkdir -p "$PYKRITA_DIR"
    
    echo "Extraindo para $PYKRITA_DIR..."
    if ! unzip -o "$TEMP_ZIP" -d "$PYKRITA_DIR"; then
        echo "Erro ao extraindo plugin."
        rm -f "$TEMP_ZIP"
        exit 1
    fi
    rm -f "$TEMP_ZIP"
    
    # FIX PERMISSIONS (Crucial if previously run as root or for Krita to see it)
    echo "STATUS: Corrigindo permissões..."
    # Ensure current user owns the Krita data directories
    chown -R "$(whoami):$(id -gn)" "$HOME/.local/share/krita"
    chown -R "$(whoami):$(id -gn)" "$HOME/.config/krita"* 2>/dev/null
    
    echo "PROGRESS: 80"

    # Python Deps
    echo "STATUS: Configurando dependências Python..."
    PIP_ARGS="--user"
    if python -m pip install --help | grep "break-system-packages" >/dev/null; then
         PIP_ARGS="--user --break-system-packages"
    fi
    
    if [ "$SKIP_TORCH_PIP" = "false" ]; then
        echo "Instalando Torch via PIP..."
        if ! python -m pip install $PIP_ARGS $PYTORCH_DEPS; then
            echo "Erro instalando torch"
            exit 1
        fi
    fi

    if ! python -m pip install $PIP_ARGS diffusers transformers accelerate; then
        echo "Erro instalando bibliotecas AI"
        exit 1
    fi
    
    echo "PROGRESS: 90"
    
    # Enable Plugin in Krita Configuration
    echo "STATUS: Ativando plugin no Krita..."
    
    # Python script to safely edit kritarc
    python3 -c "
import os

config_path = os.path.expanduser('~/.config/kritarc')
if os.path.exists(config_path):
    try:
        with open(config_path, 'r') as f:
            content = f.read()
    except:
        content = ''
else:
    content = ''

lines = content.splitlines()
output = []
in_python = False
python_found = False
enable_container_updated = False
enabled_plugins_updated = False

for line in lines:
    stripped = line.strip()
    if stripped == '[Python]':
        in_python = True
        python_found = True
        output.append(line)
        continue
    elif stripped.startswith('[') and stripped.endswith(']'):
        if in_python:
            if not enable_container_updated:
                output.append('EnablePluginContainer=true')
                enable_container_updated = True
            if not enabled_plugins_updated:
                 output.append('EnabledPlugins=ai_diffusion')
                 enabled_plugins_updated = True
        in_python = False
        output.append(line)
        continue
    
    if in_python:
        if stripped.startswith('EnablePluginContainer='):
             output.append('EnablePluginContainer=true')
             enable_container_updated = True
             continue
        if stripped.startswith('EnabledPlugins='):
             val = line.split('=', 1)[1] if '=' in line else ''
             plugins = [p.strip() for p in val.split(',') if p.strip()]
             if 'ai_diffusion' not in plugins:
                 plugins.append('ai_diffusion')
             output.append('EnabledPlugins=' + ','.join(plugins))
             enabled_plugins_updated = True
             continue
    
    output.append(line)

if not python_found:
    output.append('')
    output.append('[Python]')
    output.append('EnablePluginContainer=true')
    output.append('EnabledPlugins=ai_diffusion')
elif in_python:
    if not enable_container_updated:
        output.append('EnablePluginContainer=true')
    if not enabled_plugins_updated:
         output.append('EnabledPlugins=ai_diffusion')

with open(config_path, 'w') as f:
    f.write('\n'.join(output) + '\n')
"
    
    # Pre-configure backend
    mkdir -p "$HOME/.local/share/krita/pykrita"
    cat > "$HOME/.local/share/krita/pykrita/ai_diffusion.ini" << EOF
[Config]
backend=diffusers
device=${RENDER_MODE}
model_dir=$HOME/krita-ai-models
EOF
    # Fix permissions again for the ini file
    chown "$(whoami):$(id -gn)" "$HOME/.local/share/krita/pykrita/ai_diffusion.ini"

    # Refresh KDE system cache (might help with Krita seeing the .desktop file)
    if command -v kbuildsycoca6 &>/dev/null; then
        kbuildsycoca6 --noincremental &>/dev/null
    elif command -v kbuildsycoca5 &>/dev/null; then
        kbuildsycoca5 --noincremental &>/dev/null
    fi

    echo "PROGRESS: 100"
    echo "STATUS: Concluído"

    echo "PROGRESS: 100"
    echo "STATUS: Concluído"
}

remove_complete() {
    echo "STATUS: Removendo plugin..."
    # Remove plugin package
    pkexec pamac remove --no-confirm krita-ai-diffusion
    
    echo "STATUS: Removendo Krita..."
    # Check what is installed to remove
    if pacman -Q krita &>/dev/null; then
        pkexec pacman -Rns --noconfirm krita
    elif flatpak list | grep -q "org.kde.krita"; then
        flatpak uninstall -y org.kde.krita
    fi
    
    echo "STATUS: Limpando arquivos de configuração (Dotfiles)..."
    rm -f "$HOME/.local/share/krita/pykrita/ai_diffusion.ini"
    rm -rf "$HOME/.local/share/krita"
    rm -rf "$HOME/.config/krita"*
    rm -rf "$HOME/krita-ai-models"
    
    echo "STATUS: Remoção completa finalizada."
}

remove_plugin_only() {
    echo "STATUS: Removendo plugin (apenas pacote/config)..."
    pkexec pamac remove --no-confirm krita-ai-diffusion
    rm -f "$HOME/.local/share/krita/pykrita/ai_diffusion.ini"
    # We keep models and krita
    echo "STATUS: Plugin removido."
}

remove_gui() {
    # Default fallback if called without specifics, but we expect specific calls now
    remove_plugin_only
}

case "$1" in
    check)
        check
        ;;
    get_gpu)
        get_gpu
        ;;
    install_gui)
        install_gui "$2" "$3"
        ;;
    remove_gui)
        remove_gui
        ;;
    remove_complete)
        remove_complete
        ;;
    remove_plugin_only)
        remove_plugin_only
        ;;
    *)
        echo "Usage: $0 {check|get_gpu|install_gui|remove_gui|remove_complete|remove_plugin_only}"
        exit 1
        ;;
esac
