#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
import subprocess
import os
import locale
import gettext

# Configuração do gettext (mantém igual)
DOMAIN = 'biglinux-settings'
LOCALE_DIR = '/usr/share/locale'

locale.setlocale(locale.LC_ALL, '')
locale.bindtextdomain(DOMAIN, LOCALE_DIR)
locale.textdomain(DOMAIN)

gettext.bindtextdomain(DOMAIN, LOCALE_DIR)
gettext.textdomain(DOMAIN)
_ = gettext.gettext

class BiglinuxSettingsApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id='biglinux-settings')
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.window = SystemSettingsWindow(application=app)
        self.window.present()

class SystemSettingsWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Configurações da janela
        self.set_title(_("BigLinux Settings"))
        self.set_default_size(600, 700)

        # Diretório base dos scripts
        self.scripts_base_dir = os.path.join(os.path.dirname(__file__), '.')

        # Dicionário para mapear switches aos scripts
        self.switch_scripts = {}

        # Layout principal
        self.setup_ui()

    def setup_ui(self):
        # Container principal
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)

        # Header bar
        header_bar = Adw.HeaderBar()
        header_bar.set_title_widget(Adw.WindowTitle(title=_("BigLinux Settings")))
        main_box.append(header_bar)

        # ScrolledWindow para conteúdo
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        main_box.append(scrolled)

        # Container de conteúdo
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        content_box.set_margin_top(20)
        content_box.set_margin_bottom(20)
        content_box.set_margin_start(20)
        content_box.set_margin_end(20)
        scrolled.set_child(content_box)

        # Grupos de configurações
        self.create_usability_group(content_box)
        self.create_system_group(content_box)
        self.create_example_group(content_box)

        # Sincronizar estados após criar todos os switches
        self.sync_all_switches()

    def create_switch_with_script(self, parent_group, title, subtitle, script_name):
        """Cria um switch associado a um script"""
        row = Adw.ActionRow()
        row.set_title(title)
        row.set_subtitle(subtitle)

        switch = Gtk.Switch()
        switch.set_valign(Gtk.Align.CENTER)

        # Associar o script ao switch
        script_path = os.path.join(self.scripts_base_dir, f"{script_name}.sh")
        self.switch_scripts[switch] = script_path

        # Conectar callback
        switch.connect("state-set", self.on_switch_changed)

        row.add_suffix(switch)
        parent_group.add(row)

        return switch

    def create_usability_group(self, parent):
        """Grupo de configurações de aparência"""
        group = Adw.PreferencesGroup()
        group.set_title(_("Usability"))
        group.set_description(_("Visual system settings"))
        parent.append(group)

        # numLock
        self.num_lock_switch = self.create_switch_with_script(
            group,
            _("NumLock"),
            _("Initial NumLock state. Ignored if autologin is enabled."),
            "numLock"
        )

        # indexFiles
        self.indexfiles_switch = self.create_switch_with_script(
            group,
            _("Index Files"),
            _("Baloo, high storage I/O consumption."),
            "indexFiles"
        )

        # ssh
        self.ssh_star_switch = self.create_switch_with_script(
            group,
            _("SSH"),
            _("Enable remote access via ssh until next boot."),
            "sshStart"
        )

    def create_system_group(self, parent):
        """Grupo de configurações do sistema"""
        group = Adw.PreferencesGroup()
        group.set_title(_("System"))
        group.set_description(_("General system settings"))
        parent.append(group)

        # ssh
        self.ssh_enable_switch = self.create_switch_with_script(
            group,
            _("SSH on Boot"),
            _("Turn on ssh remote access at boot."),
            "sshEnable"
        )

    def create_example_group(self, parent):
        """Grupo de exemplo"""
        group = Adw.PreferencesGroup()
        group.set_title(_("Example"))
        group.set_description(_("Example group description"))
        parent.append(group)

        # Example
        self.example_switch = self.create_switch_with_script(
            group,
            _("Example Name"),
            _("Example description."),
            "example" # same name as the .sh file
        )

    def check_script_state(self, script_path):
        """Verifica o estado atual usando o script"""
        if not os.path.exists(script_path):
            print(_("Script not found: {}").format(script_path))
            return False

        try:
            result = subprocess.run([script_path, "check"],
                                  capture_output=True,
                                  text=True,
                                  timeout=10)

            if result.returncode == 0:
                output = result.stdout.strip().lower()
                return output == "true"
            else:
                print(_("Error checking state: {}").format(result.stderr))
                return False

        except subprocess.TimeoutExpired:
            print(_("Script timeout: {}").format(script_path))
            return False
        except Exception as e:
            print(_("Error running script {}: {}").format(script_path, e))
            return False

    def toggle_script_state(self, script_path, new_state):
        """Altera o estado usando o script"""
        if not os.path.exists(script_path):
            print(_("Script not found: {}").format(script_path))
            return False

        try:
            state_str = "true" if new_state else "false"
            result = subprocess.run([script_path, "toggle", state_str],
                                  capture_output=True,
                                  text=True,
                                  timeout=30)

            if result.returncode == 0:
                print(_("State changed successfully: {}").format(result.stdout.strip()))
                return True
            else:
                print(_("Error changing state: {}").format(result.stderr))
                return False

        except subprocess.TimeoutExpired:
            print(_("Script timeout: {}").format(script_path))
            return False
        except Exception as e:
            print(_("Error running script {}: {}").format(script_path, e))
            return False

    def sync_all_switches(self):
        """Sincroniza todos os switches com o estado atual do sistema"""
        for switch, script_path in self.switch_scripts.items():
            # Bloquear temporariamente o sinal para evitar execução do callback
            switch.handler_block_by_func(self.on_switch_changed)

            current_state = self.check_script_state(script_path)
            switch.set_active(current_state)

            # Desbloquear o sinal
            switch.handler_unblock_by_func(self.on_switch_changed)

            script_name = os.path.basename(script_path)
            print(_("Switch {} synchronized: {}").format(script_name, current_state))

    def on_switch_changed(self, switch, state):
        """Callback chamado quando qualquer switch é alterado"""
        script_path = self.switch_scripts.get(switch)

        if script_path:
            script_name = os.path.basename(script_path)
            print(_("Changing {} to {}").format(script_name, "on" if state else "off"))

            success = self.toggle_script_state(script_path, state)

            if not success:
                # Se falhou, reverter o switch
                switch.set_active(not state)
                self.show_toast(_("Failed to change setting"))

        return False

    def show_toast(self, message):
        """Mostra uma notificação toast"""
        toast = Adw.Toast()
        toast.set_title(message)
        toast.set_timeout(3)

def main():
    app = BiglinuxSettingsApp()
    return app.run()

if __name__ == "__main__":
    main()
