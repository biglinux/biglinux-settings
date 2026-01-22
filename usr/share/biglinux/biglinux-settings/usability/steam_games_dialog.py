import gi
import os
import glob
import shutil
import vdf
import threading

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gio, GObject

class SteamGameRow(GObject.Object):
    __gtype_name__ = 'SteamGameRow'
    
    appid = GObject.Property(type=str)
    name = GObject.Property(type=str)
    enabled = GObject.Property(type=bool, default=False)
    
    def __init__(self, appid, name, enabled):
        super().__init__()
        self.appid = appid
        self.name = name
        self.enabled = enabled

class SteamGamesDialog(Adw.Window):
    def __init__(self, parent=None):
        super().__init__(modal=True)
        if parent:
            self.set_transient_for(parent)
        self.set_default_size(600, 700)
        self.set_title("Steam Game Mode Options")
        
        self.steam_root = self.find_steam_root()
        self.games_store = Gio.ListStore(item_type=SteamGameRow)
        self.profiles = []
        
        # UI Structure
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)
        
        # Toolbar
        header = Adw.HeaderBar()
        main_box.append(header)
        
        # Content Area
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content_box.set_margin_top(15)
        content_box.set_margin_bottom(15)
        content_box.set_margin_start(15)
        content_box.set_margin_end(15)
        
        # Description
        desc = Gtk.Label(label="Select games to enable 'gamemoderun %command%' launch option.")
        desc.set_wrap(True)
        desc.set_halign(Gtk.Align.START)
        content_box.append(desc)
        
        # Actions Box (Check/Uncheck All)
        actions_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        btn_all = Gtk.Button(label="Check All")
        btn_all.connect("clicked", self.on_check_all)
        actions_box.append(btn_all)
        
        btn_none = Gtk.Button(label="Uncheck All")
        btn_none.connect("clicked", self.on_uncheck_all)
        actions_box.append(btn_none)
        
        content_box.append(actions_box)
        
        # List View
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_min_content_height(400)
        scrolled.add_css_class("card")
        
        self.list_view = Gtk.ListView(model=Gtk.SingleSelection(model=self.games_store))
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self.setup_list_item)
        factory.connect("bind", self.bind_list_item)
        factory.connect("unbind", self.unbind_list_item)
        self.list_view.set_factory(factory)
        
        scrolled.set_child(self.list_view)
        content_box.append(scrolled)
        
        # Status Label
        self.status_label = Gtk.Label(label="")
        self.status_label.set_halign(Gtk.Align.START)
        content_box.append(self.status_label)

        # Bottom Buttons
        bottom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        bottom_box.set_halign(Gtk.Align.END)
        
        btn_cancel = Gtk.Button(label="Cancel")
        btn_cancel.connect("clicked", lambda x: self.close())
        bottom_box.append(btn_cancel)
        
        btn_manually = Gtk.Button(label="Manually")
        btn_manually.connect("clicked", self.on_show_instructions)
        bottom_box.append(btn_manually)
        
        btn_apply = Gtk.Button(label="Apply Changes")
        btn_apply.add_css_class("suggested-action")
        btn_apply.connect("clicked", self.on_apply)
        bottom_box.append(btn_apply)
        
        content_box.append(bottom_box)
        main_box.append(content_box)
        
        # Load Data
        if not self.steam_root:
            self.status_label.set_label("Steam installation not found.")
            btn_apply.set_sensitive(False)
        else:
            threading.Thread(target=self.load_data, daemon=True).start()

    def find_steam_root(self):
        paths = [
            os.path.expanduser("~/.local/share/Steam"),
            os.path.expanduser("~/.steam/steam")
        ]
        for p in paths:
            if os.path.exists(p):
                return p
        return None

    def load_data(self):
        GLib.idle_add(self.status_label.set_label, "Loading games...")
        
        # 1. Get installed games names
        steamapps = os.path.join(self.steam_root, "steamapps")
        app_manifests = glob.glob(os.path.join(steamapps, "appmanifest_*.acf"))
        
        installed_map = {}
        for acf in app_manifests:
            try:
                with open(acf, 'r', encoding='utf-8', errors='ignore') as f:
                    data = vdf.load(f)
                app_node = data.get('AppState', {})
                appid = str(app_node.get('appid'))
                name = app_node.get('name', f"App {appid}")
                if appid:
                    installed_map[appid] = name
            except Exception as e:
                print(f"Error reading {acf}: {e}")

        # 2. Find Configs
        userdata_path = os.path.join(self.steam_root, "userdata")
        config_files = glob.glob(os.path.join(userdata_path, "*", "config", "localconfig.vdf"))
        
        self.profiles = []
        for cf in config_files:
            try:
                with open(cf, 'r', encoding='utf-8') as f:
                    data = vdf.load(f)
                self.profiles.append({'path': cf, 'data': data})
            except Exception as e:
                print(f"Error reading config {cf}: {e}")

        if not self.profiles:
            GLib.idle_add(self.status_label.set_label, "No Steam user profiles found.")
            return

        # 3. Check status in profiles
        items = []
        for appid, name in installed_map.items():
            is_enabled = False
            # If enabled in ANY profile, show as enabled
            for profile in self.profiles:
                try:
                    store = profile['data'].get('UserLocalConfigStore', {})
                    apps = store.get('Software', {}).get('Valve', {}).get('Steam', {}).get('apps', {})
                    
                    # Try direct string lookup first
                    app_data = apps.get(appid)
                    # Fallback to int lookup if needed (unlikely)
                    if not app_data:
                        try:
                            app_data = apps.get(int(appid))
                        except ValueError:
                            pass
                            
                    if isinstance(app_data, dict):
                        opts = app_data.get('LaunchOptions', '')
                        if 'gamemoderun %command%' in opts:
                            is_enabled = True
                            break
                except Exception as e:
                    print(f"Error checking profile for {appid}: {e}")
            
            items.append(SteamGameRow(appid, name, is_enabled))
            
        items.sort(key=lambda x: x.name.lower())
        
        def update_ui():
            self.games_store.remove_all()
            for item in items:
                self.games_store.append(item)
            self.status_label.set_label(f"Found {len(items)} installed games.")
            
        GLib.idle_add(update_ui)

    def setup_list_item(self, factory, list_item):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        chk = Gtk.CheckButton()
        # Keep track of binding on the widget itself to cleaning up
        chk.binding = None
        label = Gtk.Label(xalign=0)
        box.append(chk)
        box.append(label)
        list_item.set_child(box)

    def bind_list_item(self, factory, list_item):
        box = list_item.get_child()
        chk = box.get_first_child()
        label = box.get_last_child()
        item = list_item.get_item()
        
        label.set_label(item.name)
        
        # Clean previous binding if any (though unbind should have caught it)
        if hasattr(chk, 'binding') and chk.binding:
            chk.binding.unbind()
            chk.binding = None
            
        # Bind enabled property to checkbox active
        # We bind ITEM (Source) -> CHECKBOX (Target) to ensure initial state flows correct
        chk.binding = item.bind_property("enabled", chk, "active", 
                         GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)

    def unbind_list_item(self, factory, list_item):
        box = list_item.get_child()
        if box:
            chk = box.get_first_child()
            if hasattr(chk, 'binding') and chk.binding:
                chk.binding.unbind()
                chk.binding = None

    def on_check_all(self, btn):
        for i in range(self.games_store.get_n_items()):
            item = self.games_store.get_item(i)
            item.enabled = True

    def on_uncheck_all(self, btn):
        for i in range(self.games_store.get_n_items()):
            item = self.games_store.get_item(i)
            item.enabled = False

    def on_apply(self, btn):
        self.status_label.set_label("Applying changes...")
        btn.set_sensitive(False)
        threading.Thread(target=self.apply_changes, args=(btn,), daemon=True).start()

    def apply_changes(self, btn):
        count_updated = 0
        try:
            for profile in self.profiles:
                config_file = profile['path']
                data = profile['data']
                modified_this_profile = False
                
                # Navigate to apps
                try:
                    # Depending on vdf parser version, structure might vary slightly, 
                    # but usually it matches the key usage
                    store = data.get('UserLocalConfigStore', {})
                    software = store.get('Software', {})
                    valve = software.get('Valve', {})
                    steam = valve.get('Steam', {})
                    
                    if 'apps' not in steam:
                        steam['apps'] = {}
                    apps = steam['apps']
                except (KeyError, AttributeError):
                    print(f"Structure mismatch in {config_file}")
                    continue

                # Iterate UI items
                for i in range(self.games_store.get_n_items()):
                    item = self.games_store.get_item(i)
                    appid = item.appid
                    
                    # Ensure app entry exists if we are enabling
                    if appid not in apps:
                        if not item.enabled:
                            continue
                        apps[appid] = {}
                    
                    app_data = apps[appid]
                    if not isinstance(app_data, dict):
                         # If it's something weird, skip, or re-init if we really need to set it
                         if item.enabled:
                             apps[appid] = {}
                             app_data = apps[appid]
                         else:
                             continue

                    current_opts = app_data.get('LaunchOptions', '')
                    new_opts = current_opts
                    
                    CMD = "gamemoderun %command%"
                    
                    if item.enabled:
                        if CMD not in current_opts:
                            if current_opts.strip():
                                new_opts = f"{CMD} {current_opts}"
                            else:
                                new_opts = CMD
                    else:
                        if CMD in current_opts:
                             # robust removal
                            parts = current_opts.replace(CMD, "").split()
                            new_opts = " ".join(parts)
                    
                    if new_opts != current_opts:
                        app_data['LaunchOptions'] = new_opts
                        modified_this_profile = True
                        count_updated += 1

                if modified_this_profile:
                    shutil.copy(config_file, f"{config_file}.bak")
                    with open(config_file, 'w', encoding='utf-8') as f:
                        vdf.dump(data, f, pretty=True)
            
            GLib.idle_add(self.on_apply_finished, count_updated, None, btn)
            
        except Exception as e:
             GLib.idle_add(self.on_apply_finished, 0, str(e), btn)

    def on_apply_finished(self, count, error, btn):
        btn.set_sensitive(True)
        if error:
            self.show_message("Error", str(error))
        else:
            self.status_label.set_label(f"Updated {count} entries.")
            self.show_message("Success", f"{count} game entries updated across profiles.\nPlease restart Steam.", close_app=True)

    def show_message(self, title, msg, close_app=False):
        dlg = Adw.MessageDialog(heading=title, body=msg)
        dlg.add_response("ok", "OK")
        dlg.set_transient_for(self)
        if close_app:
            dlg.connect("response", lambda d, r: self.close())
        dlg.present()

    def on_show_instructions(self, btn):
        """Show Game Mode Booster Instructions in a window."""
        instructions_window = Adw.Window(modal=True, transient_for=self)
        instructions_window.set_default_size(500, 400)
        instructions_window.set_title("Game Mode Booster Instructions")
        
        # Main box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        instructions_window.set_content(main_box)
        
        # Header with Icon
        header = Adw.HeaderBar()
        
        # Add icon to header
        header_icon = Gtk.Image.new_from_icon_name("input-gaming-symbolic")
        header_icon.set_pixel_size(24)
        header.pack_start(header_icon)
        
        main_box.append(header)
        
        # Scrolled window
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        main_box.append(scroll)
        
        # Content box
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        content_box.set_margin_start(12)
        content_box.set_margin_end(12)
        content_box.set_margin_top(12)
        content_box.set_margin_bottom(12)
        scroll.set_child(content_box)
        
        # Instructions Group
        instructions_group = Adw.PreferencesGroup()
        instructions_group.set_title("Available Commands")
        content_box.append(instructions_group)
        
        # Helper to add command rows
        def add_command_row(title, command, icon):
            row = Adw.ActionRow()
            row.set_title(title)
            row.set_subtitle(command)
            row.add_prefix(Gtk.Image.new_from_icon_name(icon))
            
            # Copy Button
            from gi.repository import Gdk
            btn_copy = Gtk.Button(icon_name="edit-copy-symbolic")
            btn_copy.add_css_class("flat")
            btn_copy.set_tooltip_text("Copy to clipboard")
            btn_copy.connect("clicked", lambda b: Gdk.Display.get_default().get_clipboard().set(command))
            
            row.add_suffix(btn_copy)
            instructions_group.add(row)
        
        add_command_row("Run manually", "gamemoderun ./game", "utilities-terminal-symbolic")
        add_command_row("Steam Launch Options", "gamemoderun %command%", "input-gaming-symbolic")
        add_command_row("Older Versions", 'LD_PRELOAD="$LD_PRELOAD:/usr/$LIB/libgamemodeauto.so.0"', "focus-legacy-systray")
        
        # Close button
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, halign=Gtk.Align.CENTER)
        button_box.set_margin_top(20)
        button_box.set_margin_bottom(20)
        
        close_btn = Gtk.Button(label="Close")
        close_btn.add_css_class("pill")
        close_btn.connect("clicked", lambda b: instructions_window.close())
        button_box.append(close_btn)
        
        main_box.append(button_box)
        
        instructions_window.present()
