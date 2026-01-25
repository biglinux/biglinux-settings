
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib
import subprocess
import gettext
import threading

DOMAIN = 'biglinux-settings'
_ = gettext.gettext

class ChatAIDialog(Adw.Window):
    def __init__(self, parent_window, script_path, on_close_callback=None):
        super().__init__(modal=True, transient_for=parent_window)
        self.set_default_size(500, 300)
        self.set_title(_("ChatAI Installation"))
        
        self.script_path = script_path
        self.on_close_callback = on_close_callback
        self.is_running = False

        # Main content box
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20, margin_top=20, margin_bottom=20, margin_start=20, margin_end=20)
        self.set_content(self.main_box)

        # Header
        self.status_label = Gtk.Label(label=_("Installing ChatAI..."))
        self.status_label.add_css_class("title-3")
        self.main_box.append(self.status_label)

        # Progress Bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_hexpand(True)
        self.progress_bar.set_show_text(True)
        self.progress_bar.pulse() # Indeterminate since we don't have exact progress
        self.main_box.append(self.progress_bar)
        
        # Detail Log (Expander)
        self.log_expander = Gtk.Expander(label=_("Show Details"))
        self.log_view = Gtk.TextView()
        self.log_view.set_editable(False)
        self.log_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.log_view.set_monospace(True)
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(self.log_view)
        scrolled.set_min_content_height(150)
        self.log_expander.set_child(scrolled)
        self.main_box.append(self.log_expander)

        # Buttons
        self.button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, halign=Gtk.Align.CENTER)
        self.main_box.append(self.button_box)
        
        self.close_button = Gtk.Button(label=_("Close"))
        self.close_button.connect("clicked", self.on_close)
        self.close_button.set_visible(False)
        self.close_button.add_css_class("suggested-action")
        self.button_box.append(self.close_button)

        # Start process
        self.start_install()

    def append_log(self, text):
        buffer = self.log_view.get_buffer()
        end_iter = buffer.get_end_iter()
        buffer.insert(end_iter, text + "\n")
        # Scroll to bottom
        adj = self.log_expander.get_child().get_vadjustment()
        adj.set_value(adj.get_upper())

    def update_status(self, text):
        self.status_label.set_label(text)

    def start_install(self):
        self.is_running = True
        threading.Thread(target=self.install_thread).start()

    def install_thread(self):
        cmd = [self.script_path, "install"]
        
        # We need to read stdout line by line
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                text = line.strip()
                GLib.idle_add(self.append_log, text)
                GLib.idle_add(self.progress_bar.pulse)

        rc = process.poll()
        GLib.idle_add(self.on_install_finished, rc)

    def on_install_finished(self, return_code):
        self.is_running = False
        if return_code == 0:
            self.update_status(_("Installation Complete!"))
            self.progress_bar.set_fraction(1.0)
            self.close_button.set_visible(True)
            if self.on_close_callback:
                self.on_close_callback(True)
        else:
            self.update_status(_("Installation Failed."))
            self.close_button.set_visible(True)
            if self.on_close_callback:
                self.on_close_callback(False)

    def on_close(self, btn):
        self.close()
