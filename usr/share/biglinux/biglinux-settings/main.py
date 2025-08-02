#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
import subprocess
import os
import locale
import gettext

# Configuração do gettext
DOMAIN = 'biglinux-settings'
LOCALE_DIR = os.path.join(os.path.dirname(__file__), 'locale')

# Configurar locale do sistema
locale.setlocale(locale.LC_ALL, '')
locale.bindtextdomain(DOMAIN, LOCALE_DIR)
locale.textdomain(DOMAIN)

# Configurar gettext
gettext.bindtextdomain(DOMAIN, LOCALE_DIR)
gettext.textdomain(DOMAIN)
_ = gettext.gettext

class BiglinuxSettingsApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id='com.example.systemsettings')
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
        self.create_appearance_group(content_box)
        self.create_system_group(content_box)
        self.create_notifications_group(content_box)
        self.create_security_group(content_box)

    def create_appearance_group(self, parent):
        """Grupo de configurações de aparência"""
        group = Adw.PreferencesGroup()
        group.set_title(_("Appearance"))
        group.set_description(_("Visual system settings"))
        parent.append(group)
        
        # Tema escuro
        dark_theme_row = Adw.ActionRow()
        dark_theme_row.set_title(_("Dark Theme"))
        dark_theme_row.set_subtitle(_("Enable system dark mode"))
        dark_theme_switch = Gtk.Switch()
        dark_theme_switch.set_valign(Gtk.Align.CENTER)
        dark_theme_switch.connect("state-set", self.on_dark_theme_switched)
        dark_theme_row.add_suffix(dark_theme_switch)
        group.add(dark_theme_row)
        
        # Animações
        animations_row = Adw.ActionRow()
        animations_row.set_title(_("Animations"))
        animations_row.set_subtitle(_("Enable interface animations"))
        animations_switch = Gtk.Switch()
        animations_switch.set_valign(Gtk.Align.CENTER)
        animations_switch.set_active(True)
        animations_switch.connect("state-set", self.on_animations_switched)
        animations_row.add_suffix(animations_switch)
        group.add(animations_row)

    def create_system_group(self, parent):
        """Grupo de configurações do sistema"""
        group = Adw.PreferencesGroup()
        group.set_title(_("System"))
        group.set_description(_("General system settings"))
        parent.append(group)
        
        # Sons do sistema
        system_sounds_row = Adw.ActionRow()
        system_sounds_row.set_title(_("System Sounds"))
        system_sounds_row.set_subtitle(_("Play system event sounds"))
        sounds_switch = Gtk.Switch()
        sounds_switch.set_valign(Gtk.Align.CENTER)
        sounds_switch.set_active(True)
        sounds_switch.connect("state-set", self.on_system_sounds_switched)
        system_sounds_row.add_suffix(sounds_switch)
        group.add(system_sounds_row)
        
        # Updates automáticos
        auto_updates_row = Adw.ActionRow()
        auto_updates_row.set_title(_("Automatic Updates"))
        auto_updates_row.set_subtitle(_("Download and install updates automatically"))
        updates_switch = Gtk.Switch()
        updates_switch.set_valign(Gtk.Align.CENTER)
        updates_switch.connect("state-set", self.on_auto_updates_switched)
        auto_updates_row.add_suffix(updates_switch)
        group.add(auto_updates_row)
        
        # Telemetria
        telemetry_row = Adw.ActionRow()
        telemetry_row.set_title(_("Telemetry"))
        telemetry_row.set_subtitle(_("Send usage data for improvements"))
        telemetry_switch = Gtk.Switch()
        telemetry_switch.set_valign(Gtk.Align.CENTER)
        telemetry_switch.connect("state-set", self.on_telemetry_switched)
        telemetry_row.add_suffix(telemetry_switch)
        group.add(telemetry_row)

    def create_notifications_group(self, parent):
        """Grupo de configurações de notificações"""
        group = Adw.PreferencesGroup()
        group.set_title(_("Notifications"))
        group.set_description(_("System notification controls"))
        parent.append(group)
        
        # Notificações desktop
        desktop_notifications_row = Adw.ActionRow()
        desktop_notifications_row.set_title(_("Desktop Notifications"))
        desktop_notifications_row.set_subtitle(_("Show notifications on screen"))
        notifications_switch = Gtk.Switch()
        notifications_switch.set_valign(Gtk.Align.CENTER)
        notifications_switch.set_active(True)
        notifications_switch.connect("state-set", self.on_notifications_switched)
        desktop_notifications_row.add_suffix(notifications_switch)
        group.add(desktop_notifications_row)
        
        # Modo não perturbe
        dnd_row = Adw.ActionRow()
        dnd_row.set_title(_("Do Not Disturb"))
        dnd_row.set_subtitle(_("Silence all notifications"))
        dnd_switch = Gtk.Switch()
        dnd_switch.set_valign(Gtk.Align.CENTER)
        dnd_switch.connect("state-set", self.on_dnd_switched)
        dnd_row.add_suffix(dnd_switch)
        group.add(dnd_row)

    def create_security_group(self, parent):
        """Grupo de configurações de segurança"""
        group = Adw.PreferencesGroup()
        group.set_title(_("Security"))
        group.set_description(_("System security settings"))
        parent.append(group)
        
        # Firewall
        firewall_row = Adw.ActionRow()
        firewall_row.set_title(_("Firewall"))
        firewall_row.set_subtitle(_("Enable firewall protection"))
        firewall_switch = Gtk.Switch()
        firewall_switch.set_valign(Gtk.Align.CENTER)
        firewall_switch.connect("state-set", self.on_firewall_switched)
        firewall_row.add_suffix(firewall_switch)
        group.add(firewall_row)
        
        # Login automático
        auto_login_row = Adw.ActionRow()
        auto_login_row.set_title(_("Automatic Login"))
        auto_login_row.set_subtitle(_("Login automatically at startup"))
        auto_login_switch = Gtk.Switch()
        auto_login_switch.set_valign(Gtk.Align.CENTER)
        auto_login_switch.connect("state-set", self.on_auto_login_switched)
        auto_login_row.add_suffix(auto_login_switch)
        group.add(auto_login_row)
        
        # Bluetooth
        bluetooth_row = Adw.ActionRow()
        bluetooth_row.set_title(_("Bluetooth"))
        bluetooth_row.set_subtitle(_("Enable Bluetooth connectivity"))
        bluetooth_switch = Gtk.Switch()
        bluetooth_switch.set_valign(Gtk.Align.CENTER)
        bluetooth_switch.set_active(True)
        bluetooth_switch.connect("state-set", self.on_bluetooth_switched)
        bluetooth_row.add_suffix(bluetooth_switch)
        group.add(bluetooth_row)

    # Callbacks para os switches (com mensagens traduzidas)
    def on_dark_theme_switched(self, switch, state):
        """Callback para alternar tema escuro"""
        if state:
            print(_("Enabling dark theme..."))
            self.run_command("gsettings set org.gnome.desktop.interface gtk-theme 'Adwaita-dark'")
        else:
            print(_("Enabling light theme..."))
            self.run_command("gsettings set org.gnome.desktop.interface gtk-theme 'Adwaita'")
        return False

    def on_animations_switched(self, switch, state):
        """Callback para alternar animações"""
        if state:
            print(_("Enabling animations..."))
            self.run_command("gsettings set org.gnome.desktop.interface enable-animations true")
        else:
            print(_("Disabling animations..."))
            self.run_command("gsettings set org.gnome.desktop.interface enable-animations false")
        return False

    def on_system_sounds_switched(self, switch, state):
        """Callback para alternar sons do sistema"""
        if state:
            print(_("Enabling system sounds..."))
            self.run_command("gsettings set org.gnome.desktop.sound event-sounds true")
        else:
            print(_("Disabling system sounds..."))
            self.run_command("gsettings set org.gnome.desktop.sound event-sounds false")
        return False

    def on_auto_updates_switched(self, switch, state):
        """Callback para alternar atualizações automáticas"""
        status = _("enabled") if state else _("disabled")
        message = _("Automatic updates {}").format(status)
        print(message)
        self.show_toast(message)

    def on_telemetry_switched(self, switch, state):
        """Callback para alternar telemetria"""
        status = _("enabled") if state else _("disabled")
        message = _("Telemetry {}").format(status)
        print(message)
        self.show_toast(message)

    def on_notifications_switched(self, switch, state):
        """Callback para alternar notificações"""
        if state:
            print(_("Enabling notifications..."))
            self.run_command("gsettings set org.gnome.desktop.notifications show-banners true")
        else:
            print(_("Disabling notifications..."))
            self.run_command("gsettings set org.gnome.desktop.notifications show-banners false")
        return False

    def on_dnd_switched(self, switch, state):
        """Callback para modo não perturbe"""
        if state:
            print(_("Enabling do not disturb mode..."))
            self.run_command("gsettings set org.gnome.desktop.notifications show-banners false")
        else:
            print(_("Disabling do not disturb mode..."))
            self.run_command("gsettings set org.gnome.desktop.notifications show-banners true")
        return False

    def on_firewall_switched(self, switch, state):
        """Callback para firewall"""
        if state:
            print(_("Enabling firewall..."))
            self.run_command("pkexec ufw enable")
        else:
            print(_("Disabling firewall..."))
            self.run_command("pkexec ufw disable")
        return False

    def on_auto_login_switched(self, switch, state):
        """Callback para login automático"""
        status = _("enabled") if state else _("disabled")
        message = _("Automatic login {}").format(status)
        print(message)
        self.show_toast(message)

    def on_bluetooth_switched(self, switch, state):
        """Callback para Bluetooth"""
        if state:
            print(_("Enabling Bluetooth..."))
            self.run_command("bluetoothctl power on")
        else:
            print(_("Disabling Bluetooth..."))
            self.run_command("bluetoothctl power off")
        return False

    def run_command(self, command):
        """Executa comando do sistema"""
        try:
            result = subprocess.run(command.split(), capture_output=True, text=True)
            if result.returncode == 0:
                print(_("Command executed: {}").format(command))
            else:
                print(_("Error executing command: {}").format(result.stderr))
        except Exception as e:
            print(_("Error: {}").format(e))

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
