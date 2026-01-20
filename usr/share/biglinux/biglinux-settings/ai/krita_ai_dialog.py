
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gio
import subprocess
import os
import gettext
import threading

DOMAIN = 'biglinux-settings'
_ = gettext.gettext

class KritaAIDialog(Adw.Window):
    def __init__(self, parent_window, script_path, on_close_callback=None):
        super().__init__(modal=True, transient_for=parent_window)
        self.set_default_size(500, 300)
        self.set_title(_("Krita AI Installation"))
        
        self.script_path = script_path
        self.on_close_callback = on_close_callback
        self.is_running = False

        # Main content box
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20, margin_top=20, margin_bottom=20, margin_start=20, margin_end=20)
        self.set_content(self.main_box)

        # Header
        self.status_label = Gtk.Label(label=_("Preparing..."))
        self.status_label.add_css_class("title-3")
        self.main_box.append(self.status_label)

        # Progress Bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_hexpand(True)
        self.progress_bar.set_show_text(True)
        self.main_box.append(self.progress_bar)
        
        # Detail Log (Expander)
        self.expander = Adw.ExpanderRow(title=_("Details"))
        self.log_view = Gtk.TextView()
        self.log_view.set_editable(False)
        self.log_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.log_view.set_monospace(True)
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(self.log_view)
        scrolled.set_min_content_height(150)
        
        # We need to wrap scrolled in a box to add to expander which expects a widget
        # AdwExpanderRow adds rows, so we might just use a clamp? 
        # Actually ExpanderRow adds rows. Let's use a simpler Expander for the log.
        
        self.log_expander = Gtk.Expander(label=_("Show Details"))
        self.log_expander.set_child(scrolled)
        self.main_box.append(self.log_expander)

        # Buttons
        self.button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, halign=Gtk.Align.CENTER)
        self.main_box.append(self.button_box)
        
        self.cancel_button = Gtk.Button(label=_("Cancel"))
        self.cancel_button.connect("clicked", self.on_cancel)
        self.button_box.append(self.cancel_button)

        self.close_button = Gtk.Button(label=_("Close"))
        self.close_button.connect("clicked", self.on_close)
        self.close_button.set_visible(False)
        self.close_button.add_css_class("suggested-action")
        self.button_box.append(self.close_button)

        # Start process
        self.detect_and_start()

    def append_log(self, text):
        buffer = self.log_view.get_buffer()
        end_iter = buffer.get_end_iter()
        buffer.insert(end_iter, text + "\n")
        # Scroll to bottom
        adj = self.log_expander.get_child().get_vadjustment()
        adj.set_value(adj.get_upper())

    def update_status(self, text):
        self.status_label.set_label(text)

    def update_progress(self, fraction):
        self.progress_bar.set_fraction(fraction)

    def detect_and_start(self):
        # 1. Detect GPU (simple check, or call script check)
        # We'll run the script in 'check_gpu' mode first
        threading.Thread(target=self.check_gpu_thread).start()

    def check_gpu_thread(self):
        try:
            GLib.idle_add(self.update_status, _("Detecting GPU..."))
            process = subprocess.run([self.script_path, "get_gpu"], capture_output=True, text=True)
            gpu_type = process.stdout.strip()
            
            GLib.idle_add(self.prompt_render_mode, gpu_type)
        except Exception as e:
            GLib.idle_add(self.append_log, f"Error detecting GPU: {e}")

    def prompt_render_mode(self, gpu_type):
        if gpu_type == "Software":
            # Just proceed with software
            self.start_install("Software", "2")
            return

        # Show dialog
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading=_("Choose Render Mode"),
            body=_("GPU detected: {}. How do you want to render?").format(gpu_type)
        )
        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("cpu", _("CPU (Software)"))
        dialog.add_response("gpu", _("GPU (Recommended)"))
        
        dialog.set_default_response("gpu")
        dialog.set_close_response("cancel")
        
        dialog.connect("response", lambda d, r: self.on_render_response(d, r, gpu_type))
        dialog.present()

    def on_render_response(self, dialog, response, gpu_type):
        if response == "gpu":
            self.start_install(gpu_type, "1")
        elif response == "cpu":
            self.start_install(gpu_type, "2")
        else:
            self.close()

    def start_install(self, gpu_type, render_mode):
        self.is_running = True
        self.cancel_button.set_sensitive(False) # Too clearcut to cancel nicely for now
        threading.Thread(target=self.install_thread, args=(gpu_type, render_mode)).start()

    def install_thread(self, gpu_type, render_mode):
        # Run script with install_gui command
        GLib.idle_add(self.update_status, _("Installing..."))
        
        cmd = [self.script_path, "install_gui", gpu_type, render_mode]
        
        # We need to read stdout line by line
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                text = line.strip()
                GLib.idle_add(self.append_log, text)
                
                # Parse specific progress markers if any
                if text.startswith("PROGRESS:"):
                    try:
                        p = float(text.split(":")[1]) / 100.0
                        GLib.idle_add(self.update_progress, p)
                    except:
                        pass
                elif text.startswith("STATUS:"):
                    s = text.split(":", 1)[1].strip()
                    GLib.idle_add(self.update_status, s)

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
            self.cancel_button.set_visible(False) # Repurpose or hide

    def on_cancel(self, btn):
        self.close()

    def on_close(self, btn):
        self.close()
