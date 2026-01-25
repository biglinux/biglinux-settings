
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib
import subprocess
import gettext
import threading
import os

DOMAIN = 'biglinux-settings'
_ = gettext.gettext

class RecentFilesDialog(Adw.Window):
    """Dialog for enabling/disabling Recent Files & Locations with visual progress."""
    
    def __init__(self, parent_window, script_path, action="enable", on_close_callback=None):
        super().__init__(modal=True, transient_for=parent_window)
        self.set_default_size(550, 450)
        
        self.script_path = script_path
        self.action = action  # "enable" or "disable"
        self.on_close_callback = on_close_callback
        self.is_running = False
        self.collected_log = []

        title = _("Enabling Recent Files & Locations") if action == "enable" else _("Disabling Recent Files & Locations")
        self.set_title(title)

        # Main content box
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_content(self.main_box)

        # Header bar
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(True)
        self.main_box.append(header)

        # Content area with clamp
        clamp = Adw.Clamp(maximum_size=500, margin_top=20, margin_bottom=20, margin_start=20, margin_end=20)
        self.main_box.append(clamp)
        
        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        clamp.set_child(self.content_box)

        # Status Page (Icon and Title)
        self.status_page = Adw.StatusPage()
        self.status_page.set_title(_("Starting..."))
        self.status_page.set_icon_name("document-open-recent-symbolic")
        self.status_page.set_vexpand(False)
        self.content_box.append(self.status_page)

        # Progress Section
        progress_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.content_box.append(progress_box)

        # Progress Bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        self.progress_bar.add_css_class("osd")
        progress_box.append(self.progress_bar)

        # Status Bar (Current action)
        self.status_bar = Gtk.Label(label=_("Initializing..."))
        self.status_bar.add_css_class("caption")
        self.status_bar.add_css_class("dim-label")
        self.status_bar.set_wrap(True)
        self.status_bar.set_halign(Gtk.Align.CENTER)
        progress_box.append(self.status_bar)

        # Log View (Collapsed by default)
        self.expander = Gtk.Expander(label=_("Details"))
        self.expander.set_margin_top(10)
        self.content_box.append(self.expander)
        
        log_scroll = Gtk.ScrolledWindow()
        log_scroll.set_min_content_height(120)
        log_scroll.set_max_content_height(150)
        log_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.expander.set_child(log_scroll)
        
        self.log_view = Gtk.TextView()
        self.log_view.set_editable(False)
        self.log_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.log_view.add_css_class("monospace")
        log_scroll.set_child(self.log_view)
        
        self.log_buffer = self.log_view.get_buffer()

        # Buttons (hidden during process)
        self.button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, halign=Gtk.Align.CENTER, margin_top=20)
        self.button_box.set_visible(False)
        self.content_box.append(self.button_box)
        
        self.close_button = Gtk.Button(label=_("Close"))
        self.close_button.add_css_class("pill")
        self.close_button.add_css_class("suggested-action")
        self.close_button.connect("clicked", self.on_close_clicked)
        self.button_box.append(self.close_button)

        # Start process automatically
        self.start_process()

    def append_log(self, text):
        """Append text to the log view."""
        end_iter = self.log_buffer.get_end_iter()
        self.log_buffer.insert(end_iter, text + "\n")
        # Scroll to end
        mark = self.log_buffer.create_mark(None, self.log_buffer.get_end_iter(), False)
        self.log_view.scroll_mark_onscreen(mark)

    def update_status(self, text):
        """Update the status bar text."""
        self.status_bar.set_text(text)
        self.status_page.set_description(GLib.markup_escape_text(text))

    def update_progress(self, value):
        """Update progress bar (value 0-100)."""
        fraction = value / 100.0
        self.progress_bar.set_fraction(fraction)
        self.progress_bar.set_text(f"{int(value)}%")

    def start_process(self):
        """Start the enable/disable process in a background thread."""
        self.is_running = True
        threading.Thread(target=self.process_thread, daemon=True).start()

    def process_thread(self):
        """Execute the shell script and parse output."""
        GLib.idle_add(self.update_status, _("Starting process..."))
        
        cmd_arg = "enable_gui" if self.action == "enable" else "disable_gui"
        cmd = [self.script_path, cmd_arg]
        
        try:
            GLib.idle_add(self.append_log, f"Running: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    text = line.strip()
                    self.collected_log.append(text)
                    
                    if text.startswith("PROGRESS:"):
                        try:
                            val = float(text.split(":")[1])
                            GLib.idle_add(self.update_progress, val)
                        except:
                            pass
                    elif text.startswith("STATUS:"):
                        status_msg = text.split(":", 1)[1]
                        GLib.idle_add(self.update_status, status_msg)
                        GLib.idle_add(self.append_log, status_msg)
                    elif text.startswith("RESULT:"):
                        pass  # Handled on finish
                    else:
                        GLib.idle_add(self.append_log, text)
            
            rc = process.poll()
            GLib.idle_add(self.on_process_finished, rc)
            
        except Exception as e:
            GLib.idle_add(self.update_status, f"Error: {e}")
            GLib.idle_add(self.append_log, f"ERROR: {e}")
            GLib.idle_add(self.on_process_finished, 1)

    def on_process_finished(self, return_code):
        """Handle process completion."""
        self.is_running = False
        
        if return_code == 0:
            self.show_success_view()
            if self.on_close_callback:
                self.on_close_callback(True)
        elif return_code == 126 or return_code == 127:
            self.status_page.set_title(_("Cancelled"))
            self.status_page.set_description(_("Operation was cancelled."))
            self.status_page.set_icon_name("dialog-warning-symbolic")
            self.button_box.set_visible(True)
            if self.on_close_callback:
                self.on_close_callback(False)
        else:
            self.status_page.set_title(_("Failed"))
            self.status_page.set_description(_("Process failed. Check details for more info."))
            self.status_page.set_icon_name("dialog-error-symbolic")
            self.button_box.set_visible(True)
            if self.on_close_callback:
                self.on_close_callback(False)

    def show_success_view(self):
        """Show success message with restart warning."""
        if self.action == "enable":
            self.status_page.set_title(_("Recent Files & Locations Enabled"))
            self.status_page.set_icon_name("emblem-ok-symbolic")
        else:
            self.status_page.set_title(_("Recent Files & Locations Disabled"))
            self.status_page.set_icon_name("emblem-ok-symbolic")
        
        self.update_progress(100)
        
        # Show warning message
        warning_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12, margin_top=16)
        warning_box.add_css_class("card")
        warning_box.set_margin_start(8)
        warning_box.set_margin_end(8)
        
        # Warning header
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, margin_top=12, margin_start=12, margin_end=12)
        warning_icon = Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
        warning_icon.add_css_class("warning")
        header_box.append(warning_icon)
        
        warning_title = Gtk.Label(label=_("Important"))
        warning_title.add_css_class("heading")
        header_box.append(warning_title)
        warning_box.append(header_box)
        
        # Warning messages
        messages_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, margin_start=12, margin_end=12, margin_bottom=12)
        
        msg1 = Gtk.Label(label=_("• To fully apply changes, restart your computer."))
        msg1.set_wrap(True)
        msg1.set_xalign(0)
        msg1.add_css_class("caption")
        messages_box.append(msg1)
        
        msg2 = Gtk.Label(label=_("• Dolphin creates a visual cache. Close it completely and reopen for recent files/locations to appear."))
        msg2.set_wrap(True)
        msg2.set_xalign(0)
        msg2.add_css_class("caption")
        messages_box.append(msg2)
        
        warning_box.append(messages_box)
        
        # Insert warning before buttons
        self.content_box.insert_child_after(warning_box, self.expander)
        
        # Show close button
        self.button_box.set_visible(True)

    def on_close_clicked(self, button):
        """Handle close button click."""
        self.close()
